from PIL import Image, ImageDraw, ImageFont
import sys
import os
from os import path

config = {
    "style": {
        "a": 1,
    }
}

curDir = path.dirname(path.abspath(__file__))
[fullWidth, fullHeight] = (500, 1500)
def partition(arr, n):
    ret = []
    sub_arr = []
    counter = 0
    l = len(arr)
    for i in range(l):
        counter += 1
        if counter <= n:
            sub_arr.append(arr[i])
        if counter == n or i == l - 1:
            ret.append(sub_arr)
            counter = 0
            sub_arr = []
    return ret


# 生成1个菜
def genMenu(imageDir, menuName):
    fullMenuDir = path.join(imageDir, menuName)
    print('fullMenuDir', fullMenuDir)
    toImg = Image.new('RGBA', (fullWidth, fullHeight))
    for matFile in os.listdir(fullMenuDir):
        [name, ext] = path.splitext(matFile)
        print(name, ext)

        #
        draw = ImageDraw.Draw(toImg)

        # 标题绘制
        # font = ImageFont.truetype('Arial Bold Italic.ttf', 48)
        # todo sr 换成: 思源宋体bold
        fontTitle = ImageFont.truetype('SourceHanSerifCN-Bold', 48) # 不写.ttf后缀会自动搜索非.ttf字体

        fillColorTitle = '#333'
        [lineWidthTitle, lineHeightTitle] = draw.textsize(menuName, font=fontTitle)
        print('[lineWidth, lineHeight]', [lineWidthTitle, lineHeightTitle])
        # 注意坑, 这里的align只相对字体所占最大宽度定位居中, 不相对画布居中
        draw.text( ((fullWidth - lineWidthTitle) / 2, (160 - lineHeightTitle) / 2), menuName, font=fontTitle, fill=fillColorTitle, align="center")

        # 主菜绘制
        if name == 'main':
            mainImg = Image.open(path.join(fullMenuDir, matFile))
            mainImg.resize((600, 450), Image.ANTIALIAS)
            toImg.paste(mainImg, (0, 160))

        # 描述文案绘制
        fontDesc = ImageFont.truetype('SourceHanSerifCN-Bold', 24)
        fillColorDesc = '#333'

        desc = ''
        if name == 'desc':
            with open(path.join(fullMenuDir, matFile), 'r') as descFile:
                desc = descFile.read()

            # 分行
            [lineWidthDesc, lineHeightDesc] = draw.textsize(desc, font=fontDesc)
            linesDesc = lineWidthDesc / (650 - 28 * 2 - 160) # 最后的减为调整: 未能领悟pillow是如何计算行宽
            descArr = partition(desc, int(len(desc) / linesDesc))
            descStrArr = map(lambda arr: ''.join(arr), descArr)
            processedDescStr = '\n'.join(descStrArr)
            draw.multiline_text((28, 650), processedDescStr, font=fontDesc, fill=fillColorDesc, align="left")


        # 绘制子菜
        # draw.ellipse((350, 50, 400, 100), 'seagreen', 'skyblue')


        toImg.show()
        toImg.save(path.join(imageDir, '../output/' + menuName) + '.png')



        # fromImg.
        # toImg.paste(fromImg, ())

    # todo sr realdata outfile
    # toImg.show()
    # toImg.save('./output/菜品_xx.png')

def circle_new():
    ima = Image.open("images/菜名_xx/main.jpg").convert("RGBA")

    size = ima.size

    r2 = min(size[0], size[1])

    if size[0] != size[1]:

        ima = ima.resize((r2, r2), Image.ANTIALIAS)

    circle = Image.new('L', (r2, r2), 0)

    draw = ImageDraw.Draw(circle)

    draw.ellipse((0, 0, r2, r2), fill=255)

    alpha = Image.new('L', (r2, r2), 255)

    alpha.paste(circle, (0, 0))

    ima.putalpha(alpha)

    ima.save('test_circle.png')

def readMaterialsAndDraw(imageDir):
    for menuName in os.listdir(imageDir):
        fullMenuDir = path.join(imageDir, menuName)
        if path.isdir(fullMenuDir):
            genMenu(imageDir, menuName)

def gen():
    readMaterialsAndDraw(path.join(curDir, 'images'))

if __name__ == '__main__':
    # gen()
    circle_new()




