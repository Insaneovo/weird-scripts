# 代码的很多地方可读性非常差
# 懒得改了 直接发了

from playwright.sync_api import sync_playwright, Playwright , _generated
import json
import random
from time import sleep


filter_rules = []

debug = False

def new_game(page: _generated.Page) -> int:
    rt = random.choice(targets)
    print('-'*30 + "\n开始输入试探词" , rt)
    inputNewWord(page, rt)

    for i in range(6):
        accepted = filterWords(page)
        if accepted['success'] :
            print("赢一把！！！")
            page.locator('button').get_by_text("new game").click()
            return 1
        elif i == 5:
            print("输一把！！！")
            if debug:
                input()
            page.locator('button').get_by_text("new game").click()
            return 0
        if len(accepted["words"]) > 0:
            rt = random.choice(accepted["words"])
            inputNewWord(page, rt)
            print("输入单词：",rt)


        else:
            print("Damn!!!")
            print(accepted["rules"])
            if debug:
                input()

def inputNewWord(page : _generated.Page , word, check : bool = True):
    for char in word:
        page.locator(".Game-keyboard-button").get_by_text(char,exact=True).click()
    page.locator(".Game-keyboard-button").get_by_text("Enter").click()

def filterWords(page : _generated.Page) -> dict:
    rules = checkStatus(page)
    if rules['success']:
        return {"success":True}
    else:
        rules = rules['rules']
    results = []
    for target in targets:
        broken = False
        for rule in rules['no']:
            if rule.lower() in target:
                broken = True
                break
        if broken:
            continue
        for rule in rules['correct']:
            if target[rule['pos']] != rule['letter'].lower():
                broken = True
                break
        if broken:
            continue
        for rule in rules['elsewhere']:
            if rule['letter'].lower() not in target or target[rule['pos']] == rule['letter'].lower():
                broken = True
                break
        if broken:
            continue
        # for rule in rules['norepeat']:
        #     if target.count(rule['letter'].lower()) > rule['times']:
        #         broken = True
        #         break
        # if broken:
        #     continue
        results.append(target)
    # print(results)
    #
    # words = set()
    # [words.add(r) for r in rules['no']]
    # [words.add(r['letter']) for r in rules['elsewhere']]
    # [words.add(r['letter']) for r in rules['correct']]

    return {"success":False,"words":results,"rules":rules}

def checkStatus(page : _generated.Page):
    try:
        sleep(1)
        rules = {"correct":[],"elsewhere":[],"no":[]}

        all_locked_rows = page.query_selector_all(".Row-locked-in")
        for locked_rows in all_locked_rows:
            for i , div in enumerate(locked_rows.query_selector_all("div")):
                position_status = div.get_attribute("class").split()[1].replace("letter-","")
                if position_status == "absent":
                    rules['no'].append([div.inner_text(),i])
                else:
                    if not (position_status == "correct" and {"letter":div.inner_text(),"pos":i} in rules["correct"]):
                        if {"letter":div.inner_text(),"pos":i} not in rules[position_status]:
                            rules[position_status].append({"letter":div.inner_text(),"pos":i})
                    # print(div.inner_text(), position_status , i)
        correct_letters = [ le['letter'] for le in rules["correct"]]
        # rules["elsewhere"] = [ rule for rule in rules["elsewhere"] if rule["letter"]  not in correct_letters]
        elsewhere_letters = [ le['letter'] for le in rules["elsewhere"]]
        # rules["norepeat"]  = set([rule  for rule in rules["no"] if rule in correct_letters])
        # rules['norepeat'] = [ {"letter":rule,"times":correct_letters.count(rule) } for rule in rules['norepeat'] ]
        # rules['no'] = set([rule for rule in rules["no"] if rule not in correct_letters and rule not in elsewhere_letters])
        tmp = set()
        for rule in rules['no']:
            if rule[0] in correct_letters or rule[0] in elsewhere_letters:
               rules['elsewhere'].append({"letter":rule[0],"pos":rule[1]})
            else:
                tmp.add(rule[0])
        rules['no'] = tmp
        result = {"success": (True if len(rules['correct']) >= 5 else False) , "rules": rules}
        if debug:
            print(result)
        return result


    except IndexError as e:
        checkStatus(page)

def run(playwright : Playwright):
    browser = playwright.chromium.launch(headless=False)
    content = browser.new_context(viewport={"width":500,"height":600})
    page = content.new_page()
    # page.set_viewport_size({"width": 800, "height": 600})
    print("开始载入页面")
    page.goto("https://wordly.org/",wait_until="commit")
    print("等待页面载入完成...")
    page.get_by_text("Guess the first word").wait_for(timeout=60000)

    while True:
        code = new_game(page)
        sleep(1.5)

    content.close()
    browser.close()

with open("five.json",'r') as f:
    targets =  json.load(f)
    with sync_playwright() as playwright:
        run(playwright)
