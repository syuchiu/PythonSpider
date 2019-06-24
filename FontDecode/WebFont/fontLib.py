import random

from fontTools import ttx
from fontTools.ttLib import TTFont


def random_unicode(lengths):  # 随机生成Unicode字符集
    while True:

        shuma = ((str(random.sample(random_list, int(lengths))).replace('\'', '')).replace(',', '')).replace(' ', '') \
            .replace('[', '').replace(']', '')

        # print("shuma:", shuma)
        # Python isalpha() 方法检测字符串是否只由字母组成。若是则直接返回
        if shuma[0].isalpha():
            return shuma
        else:
            continue


def TTFontsXML(filenames):  # 转换成XMl 到临时目录
    filenametemp = "temp/basefont.xml"
    font = TTFont(filenames)
    font.saveXML(filenametemp)
    return filenametemp


def TTFonts(filenames):  # 转换XML转换ttf
    try:
        print("开始转换字体！！！" + filenames)
        ttx.main([filenames])
        print("-----------------------------------")
    except Exception as e:
        print("Something went wrong converting ttx -> ttf/otf:")
        exit()


def Editfile(fontsjson, files):
    # 生成XML文件名
    random_list = ["a", "v", "x", "s", "q", "w", "e", "r", "t", "y", "u", "i", "o", "z", "x", "c", "v", "b", "n", "m",
                   "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ]

    shuma = ((str(random.sample(random_list, int(25))).replace('\'', '')).replace(',', '')). \
        replace(' ', '').replace('[', '').replace(']', '')

    filenametemp = "temp/" + shuma + ".xml"

    try:
        with open(files, 'r+') as fileOpen:
            data = fileOpen.read()
            fileOpen.close()

        # 映射替换并写入TTF文件
        for key in fontsjson.keys():
            data = data.replace(str(relationdic[key]), str(fontsjson[key]))

            data = data.replace(str(relationdic[key]).upper(), str(fontsjson[key]).upper())

        with open(filenametemp, 'w') as f:
            f.write(data)
            f.close()

        return shuma + ".ttf", filenametemp

    except Exception as ex:
        filenametemp = "error"
        filenames = ""
        return filenametemp, filenames


if __name__ == '__main__':
    # random_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    random_list = ['e', 'a', 'd', 'f', 'c', 'b', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    ttf_patn = "fontello.woff"  # 请输入ttf文件绝对路径:

    unicodelengths = 4  # 输入 UniCode 长度:

    ttfnumber = 3  # 输入生成多少个文件:

    relationdic = {'W': 'e800', "H": 'e801', "D": 'e803', "E": 'e805'}
    try:
        macs = len(relationdic) + 50 * ttfnumber  # 可能会有重复 多加点

        tem_list = []

        for x in range(0, int(macs)):
            tem_list.append(random_unicode(unicodelengths))

        #
        tem_list = list(set(tem_list))  # 去重

        tempfontsxmlpa = TTFontsXML(ttf_patn)  # 转换到临时XML地址。

        okjson = []

        # 循环10次
        for f in range(0, ttfnumber):

            relationdictemp = relationdic.copy()

            for key in relationdictemp.keys():
                # print("tem_list:", tem_list)
                # 4选1 0-N
                b = random.sample(tem_list, 1)
                # 移除被选中的
                tem_list.remove(b[0])

                relationdictemp[key] = b[0]

            print(relationdictemp)
            # 转换的XML文件
            filenames, filenametemp = Editfile(relationdictemp, tempfontsxmlpa)

            if filenametemp != "error":  # 如果返回修改成功 启动转换ttf的程序！

                TTFonts(filenametemp)

                jsonSeve = {"url": filenames, "data": relationdictemp}

                okjson.append(jsonSeve)

                print("okJson:", okjson)

    except Exception as e:
        pass
