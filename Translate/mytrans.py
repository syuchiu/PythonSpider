from youdao import YouDao, appVersion
from baiduTrans import BaiduTranslate
from googleTrans import GoogleTrans

if __name__ == '__main__':
    word = input("需要翻译的单词:")
    to = input("翻译语言en/zh：")
    y = YouDao(word, appVersion)
    y.run()
    print("====" * 20)
    b = BaiduTranslate(word, to)
    b.run()
    print("====" * 20)
    if to == 'zh':
        googleTo = "zh-CN"
    else:
        googleTo = to
    g = GoogleTrans(word, googleTo)
    g.run()
