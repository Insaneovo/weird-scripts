# 代码的很多地方可读性非常差
# 懒得改了 直接发了

from playwright.sync_api import sync_playwright, Playwright , _generated
import json
import random
from time import sleep


filter_rules = []

def new_game(page: _generated.Page) -> int:
    rt = random.choice(targets)
    print("开始输入试探词" , rt)
    inputNewWord(page, rt)

    for i in range(7):
        if i == 6:
            page.locator('button').get_by_text("new game").click()
            return 0
        accepted = filterWords(page)
        if len(accepted[0]) > 1:
            # if len(accepted[0]) > 5 and i > 2 and len(accepted[1]) < 9:
            #     ok = False
            #     for target in targets:
            #         if len([ac for ac in accepted[1] if ac in target]) == 0:
            #             inputNewWord(page,target)
            #             ok = True
            #     if not ok:
            #         inputNewWord(page, random.choice(accepted[0]))
            # else:
            #     inputNewWord(page,random.choice(accepted[0]))
            rt = random.choice(accepted[0])
            inputNewWord(page, rt)
            print("输入单词：",rt)
        elif len(accepted[0]) > 0:
            if accepted[0][0] == 'enter':
                page.locator('button').get_by_text("new game").click()
                return 1
            else:
                inputNewWord(page,accepted[0][0])
                print("输入单词：", accepted[0][0])

        else:
            print("Damn!!!")
            print(accepted[2])
            input()

def inputNewWord(page : _generated.Page , word, check : bool = True):
    for char in word:
        page.locator(".Game-keyboard-button").get_by_text(char,exact=True).click()
    page.locator(".Game-keyboard-button").get_by_text("Enter").click()

def filterWords(page : _generated.Page) -> list:
    rules = checkStatus(page)
    if rules['success']:
        return [["enter"]]
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
        for rule in rules['norepeat']:
            if target.count(rule.lower()) > 1:
                broken = True
                break
        if broken:
            continue
        results.append(target)
    # print(results)

    words = set()
    [words.add(r) for r in rules['no']]
    [words.add(r['letter']) for r in rules['elsewhere']]
    [words.add(r['letter']) for r in rules['correct']]

    return [results,words,rules]

def checkStatus(page : _generated.Page):
    try:
        sleep(1)
        rules = {"correct":[],"elsewhere":[],"no":set(),"norepeat":set()}

        all_locked_rows = page.query_selector_all(".Row-locked-in")
        for locked_rows in all_locked_rows:
            for i , div in enumerate(locked_rows.query_selector_all("div")):
                position_status = div.get_attribute("class").split()[1].replace("letter-","")
                if position_status == "absent":
                    rules['no'].add(div.inner_text())
                else:
                    if not (position_status == "correct" and {"letter":div.inner_text(),"pos":i} in rules["correct"]):
                        rules[position_status].append({"letter":div.inner_text(),"pos":i})
                    # print(div.inner_text(), position_status , i)
        correct_letters = [ le['letter'] for le in rules["correct"]]
        rules["elsewhere"] = [ rule for rule in rules["elsewhere"] if rule["letter"]  not in correct_letters]
        elsewhere_letters = [ le['letter'] for le in rules["elsewhere"]]
        rules["norepeat"]  = set([rule  for rule in rules["no"] if rule in correct_letters])
        rules['no'] = set([rule for rule in rules["no"] if rule not in correct_letters and rule not in elsewhere_letters])
        result = {"success": (True if len(rules['correct']) >= 5 else False) , "rules": rules}
        # print(result)
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
    page.get_by_text("Guess the first word").wait_for(timeout=30000)

    while True:
        print( "赢一把" if new_game(page) == 1 else "输一把")
        sleep(1.5)
        # input()

    content.close()
    browser.close()

with open("five.json",'r') as f:
    targets =  json.load(f)
    with sync_playwright() as playwright:
        run(playwright)
