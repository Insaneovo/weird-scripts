# 使用说明

这是一个用来自动玩 wordle.org 的脚本，基于 Playwright 编写。

## 使用步骤

1. 安装 Playwright：  
   pip install playwright

2. 下载浏览器：  
   playwright install

3. 运行脚本：  
   确保 five.json 文件和脚本在同一目录下，然后运行：  
   python wordle-bot.py

## 注意

- five.json 是一个包含五字母单词的 JSON 文件，脚本依赖它来猜词。
- 本项目仅供学习使用。
