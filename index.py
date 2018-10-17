from PIL import Image, ImageDraw, ImageFont
import sys
import os
from os import path
import re
import math

config = {
    "style": {
        "full_width": 600,
        "full_height": 1500,
        "desc_padding_left": 28,
        "desc_spacing": 6,
        "c_radius": 196,
        "c_children_radius": 55,
        'c_and_children_border_color': 'purple',
    }
}

curDir = path.dirname(path.abspath(__file__))

style = config['style']
full_width = style['full_width']
full_height = style['full_height']
desc_padding_left = style['desc_padding_left']
desc_spacing = style['desc_spacing']
c_radius = style['c_radius']
c_children_radius =style['c_children_radius']
c_and_children_border_color = style['c_and_children_border_color']

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
def gen_menu(image_dir, menu_name):
    full_menu_dir = path.join(image_dir, menu_name)
    print('fullMenuDir', full_menu_dir)
    to_img = Image.new('RGBA', (full_width, full_height))
    draw = ImageDraw.Draw(to_img)

    # 遍历文件夹生成菜材料数据
    mat_config = {'c_children_name_arr': []}
    '''
    mat_config demo
   {
   'c_children_name_arr': [
     {'name': '朝天椒', 'sort': 0}, 
     {'name': '胡萝卜', 'sort': 1}, 
     {'name': '孜然', 'sort': 2}, 
     {'name': '大排', 'sort': -1}
   ], 
   'desc': {'file': '/Users/a/projs/image_gen/images/孜香大排/desc.txt'}, 
   'main': {'file': '/Users/a/projs/image_gen/images/孜香大排/main.jpg'},
   'c': {'file': '/Users/a/projs/image_gen/images/孜香大排/c_大排.png'}, 
   'c0': {'file': '/Users/a/projs/image_gen/images/孜香大排/c0_朝天椒.png'}, 
   'c1': {'file': '/Users/a/projs/image_gen/images/孜香大排/c1_胡萝卜.png'}, 
   'c2': {'file': '/Users/a/projs/image_gen/images/孜香大排/c2_孜然.png'}
   
   }
    '''
    for mat_file in os.listdir(full_menu_dir):
        [name, ext] = path.splitext(mat_file)
        abs_mat_file = path.join(full_menu_dir, mat_file)
        if name == 'main':
            mat_config['main'] = {"file": abs_mat_file}
        elif name == 'desc':
            mat_config['desc'] = {"file": abs_mat_file}
        elif str.startswith(name, 'c0_'):
            mat_config['c0'] = {'file': abs_mat_file}
            mat_config['c_children_name_arr'].append({'name': re.sub('^c0_', '', name), "sort": 0})
        elif str.startswith(name, 'c1_'):
            mat_config['c1'] = {'file': abs_mat_file}
            mat_config['c_children_name_arr'].append({'name': re.sub('^c1_', '', name), "sort": 1})
        elif str.startswith(name, 'c2_'):
            mat_config['c2'] = {'file': abs_mat_file}
            mat_config['c_children_name_arr'].append({'name': re.sub('^c2_', '', name), "sort": 2})
        elif str.startswith(name, 'c_'):
            mat_config['c'] = {"file": abs_mat_file}
            mat_config['c_children_name_arr'].append({'name': re.sub('^c_', '', name), "sort": -1})

    print('%s menu_mat_config %s' %(menu_name, mat_config))


    # for mat_file in os.listdir(full_menu_dir):
    #     [name, ext] = path.splitext(mat_file)
    #     print(name, ext)

    # 绘制背景
    draw.rectangle((0, 0, full_width, full_height), 'white')

    # 标题绘制, top_0-160_mid
    font_title = ImageFont.truetype('SourceHanSerifCN-Bold', 48) # 不写.ttf后缀会自动搜索非.ttf字体
    text_color_normal = '#333'
    [line_width_title, line_height_title] = draw.textsize(menu_name, font=font_title)
    # 注意坑, 这里的align只相对字体所占最大宽度定位居中, 不相对画布居中
    draw.text(((full_width - line_width_title) / 2, (160 - line_height_title - 10) / 2), menu_name, font=font_title, fill=text_color_normal, align="center")

    # 主菜绘制, top_160
    main_img = Image.open(mat_config['main']['file'])
    main_img.resize((full_width, 450), Image.ANTIALIAS)
    to_img.paste(main_img, (0, 160))

    # 描述文案绘制, top_650
    font_desc = ImageFont.truetype('SourceHanSerifCN-Bold', 24)
    fill_color_desc = '#333'
    desc = ''
    with open(mat_config['desc']['file'], 'r') as descFile:
        desc = descFile.read()
    # 分行
    [line_width_desc, line_height_desc] = draw.textsize(desc, font=font_desc, spacing=desc_spacing)
    print('[line_width_desc, line_height_desc]', [line_width_desc, line_height_desc])
    lines_desc = line_width_desc / (full_width - desc_padding_left * 2 - 40) # 最后的减为调整: 未能领悟pillow是如何计算行宽
    desc_arr = partition(desc, int(len(desc) / lines_desc))
    desc_str_arr = map(lambda arr: ''.join(arr), desc_arr)
    processed_desc_str = '\n'.join(desc_str_arr)
    [line_width_processed_desc, line_height_processed_desc] = draw.textsize(processed_desc_str, font=font_desc)
    line_height_processed_desc = 68
    print('[line_width_processed_desc, line_height_processed_desc]', [line_width_processed_desc, line_height_processed_desc])
    draw.multiline_text((30, 640), processed_desc_str, font=font_desc, fill=fill_color_desc, align="left", spacing=desc_spacing)

    # 子菜绘制
    ## 主子菜
    c_top = int(650 + line_height_processed_desc * int(lines_desc) - desc_spacing);
    int_lines_desc = math.ceil(lines_desc)
    print('int_lines_desc %i' % int_lines_desc)
    if int_lines_desc == 1:
        c_top += 70;
    elif int_lines_desc == 2:
        c_top += 40;
    elif int_lines_desc == 3:
        pass
    elif int_lines_desc == 4:
        c_top -= 20;
        pass

    c0_top = int(c_top + 326)
    c1_top = int(c_top + c_radius * 2 + 30)
    c2_top = c0_top

    if 'c' in mat_config:

        # drawCircleAvatar(avatar, to_img)
        draw_circle(c_radius * 2, mat_config['c']['file'], to_img, (int(full_width / 2 - c_radius), c_top), outline_color = c_and_children_border_color, outline_width = 4)

    ## 子菜0-2 0_left 1_mid 2_right
    if 'c0' in mat_config:
        draw_circle(c_children_radius * 2, mat_config['c0']['file'], to_img, (42, c0_top), outline_color = c_and_children_border_color, outline_width = 2)

    if 'c1' in mat_config:
        draw_circle(c_children_radius * 2, mat_config['c1']['file'], to_img, (int(full_width / 2 - c_children_radius), c1_top), outline_color = c_and_children_border_color, outline_width = 2)
    if 'c2' in mat_config:
        draw_circle(c_children_radius * 2, mat_config['c2']['file'], to_img, (int(full_width - c_children_radius * 2 - 30), c2_top), outline_color = c_and_children_border_color, outline_width = 2)

    # circle_new(to_img, (int(full_width / 2 - c_radius), c_top))
    avatar = Image.open('images/孜香大排/main.jpg')

    # 底部品名 配料表
    foot_desc_1_title = '品名'
    foot_desc_1_text = menu_name
    foot_desc_2_title = '配料表'
    foot_desc_2_text  = ' '.join(map(lambda c_child: c_child['name'], sorted(mat_config['c_children_name_arr'], key=lambda item: item['sort'])))

    foot_desc_line_1_top = c_top + c_radius * 2 + 30 +  c_children_radius * 2 + 40
    for i in range(3):
        y = foot_desc_line_1_top + 38 * i
        draw.line((28, y, full_width - 28 * 2, y), '#f4efea', 1)


    font_foot_desc = ImageFont.truetype('SourceHanSerifCN-Bold', 22)
    text_color_desc_title = '#808080'
    draw.text((28, foot_desc_line_1_top + 2), foot_desc_1_title, font=font_foot_desc, fill=text_color_desc_title, align="center")
    draw.text((150, foot_desc_line_1_top + 2), foot_desc_1_text, font=font_foot_desc, fill=text_color_normal, align="center")
    draw.text((28, foot_desc_line_1_top + 2 + 38), foot_desc_2_title, font=font_foot_desc, fill=text_color_desc_title, align="center")
    draw.text((150, foot_desc_line_1_top + 2 + 38), foot_desc_2_text, font=font_foot_desc, fill=text_color_normal, align="center")



    # toImg.show()
    to_img.save(path.join(image_dir, '../output/' + menu_name) + '.png')

'''
# 画圆的可用_能理解版本
def draw_circle_2(w, path, to_img, to_xy, outline_color = None, outline_width = 0):
    im = Image.open(path).convert("RGBA")
    im.resize((w, w), Image.ANTIALIAS)
    # im.resize((100, 100), Image.ANTIALIAS)
    print('xxx_pre', im.size, (w, w))
    #遮罩对象
    mask = Image.new('L', (w,w), 0)
    draw = ImageDraw.Draw(mask)
    # mask内圆
    w_minus_outline_width = w - outline_width
    draw.ellipse((outline_width, outline_width, w_minus_outline_width, w_minus_outline_width), fill=255)
    # mask外环
    draw.ellipse((0, 0) + (w, w), fill=None, outline=outline_color, width=outline_width)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    print('xxx', im.size, (w, w), to_xy)
    im.putalpha(mask)
    to_img.paste(im, to_xy, im)
    # im.save('test-11.png')
'''

'''
def circle_new(to_img, to_xy):
    ima = Image.open("images/孜香大排/c_大排.png").convert("RGBA")

    size = ima.size

    r2 = min(size[0], size[1])

    if size[0] != size[1]:

        ima = ima.resize((r2, r2), Image.ANTIALIAS)

    circle = Image.new('L', (r2, r2), 0)

    draw = ImageDraw.Draw(circle)
    # draw.rectangle((0, 0, r2, r2), 'white')

    draw.ellipse((0, 0, r2, r2), fill=255)

    alpha = Image.new('L', (r2, r2), 255)

    alpha.paste(circle, (0, 0))

    ima.putalpha(alpha)
    to_img.putalpha(alpha)

    to_img.paste(ima, to_xy)
    ima.save('test_circle.png')
'''

# 改图片颜色改outline_color即可
def draw_circle(w, path, to_img, to_xy, outline_color = None, outline_width = 0):
    (x, y) = (0, 0)
    ima = Image.open(path).convert("RGBA")

    ima = ima.resize((w, w), Image.ANTIALIAS)

    circle = Image.new('L', (w, w), 0)

    draw = ImageDraw.Draw(circle)

    w_minus_outline_width = w - outline_width
    draw.ellipse((outline_width, outline_width, w_minus_outline_width, w_minus_outline_width), fill=255)
    # mask外环
    draw.ellipse((0, 0) + (w, w), fill=None, outline=outline_color, width=outline_width)

    alpha = Image.new('L', (w, w), 255)

    alpha.paste(circle, (0, 0))
    #
    ima.putalpha(alpha)
    to_img.paste(ima, to_xy, ima)

def read_materials_and_draw_menus(image_dir):
    for menuName in os.listdir(image_dir):
        full_menu_dir = path.join(image_dir, menuName)
        if path.isdir(full_menu_dir):
            gen_menu(image_dir, menuName)

def gen():
    read_materials_and_draw_menus(path.join(curDir, 'images'))

'''
def circle2(path, #to_img, to_xy, outline_color = None, outline_width = 0
            ):
    ima = Image.open(path).convert("RGBA")

    size = ima.size

    # 因为是要圆形，所以需要正方形的图片

    r2 = min(size[0], size[1])

    if size[0] != size[1]:

        ima = ima.resize((r2, r2), Image.ANTIALIAS)

    imb = Image.new('RGBA', (r2, r2),(255,255,255,0))
    draw = ImageDraw.Draw(imb)
    draw.rectangle((0, 0, r2, r2), 'white')

    pima = ima.load()

    pimb = imb.load()

    r = float(r2/2) #圆心横坐标

    for i in range(r2):

        for j in range(r2):

            lx = abs(i-r+0.5) #到圆心距离的横坐标

            ly = abs(j-r+0.5)#到圆心距离的纵坐标

            l  = pow(lx,2) + pow(ly,2)

            if l <= pow(r, 2):

                pimb[i,j] = pima[i,j]
    imb.resize((r2, r2), Image.ANTIALIAS)

    imb.save("test_circle.png")
'''

if __name__ == '__main__':
    gen()
    # circle_corder_image();
    # circle2("images/孜香大排/c1_胡萝卜.png")
    # draw_circle((0, 0),  255, "images/孜香大排/c_大排.png",)
    # circle_new()




