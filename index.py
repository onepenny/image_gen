from PIL import Image, ImageDraw, ImageFont
import sys
import os
from os import path
import re
import math
import json

config = {
    "style": {
        "full_width": 600,
        "full_height": 1500,
        "desc_padding_left": 28,
        "desc_spacing": 14,
        "c_radius": 196,
        "c_children_radius": 55,
        "c_and_children_border_color": "white",
        "c_border_path": "common_images/c_border.png",
        "c_child_border_path": "common_images/c_child_border.png",
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
c_border_path = style['c_border_path']
c_child_border_path = style['c_child_border_path']

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
    # print('fullMenuDir', full_menu_dir)


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
        elif str.startswith(name, 'c0'):
            mat_config['c0'] = {'file': abs_mat_file}
            mat_config['c_children_name_arr'].append({'name': re.sub('^c0', '', name), "sort": 0})
        elif str.startswith(name, 'c1'):
            mat_config['c1'] = {'file': abs_mat_file}
            mat_config['c_children_name_arr'].append({'name': re.sub('^c1', '', name), "sort": 1})
        elif str.startswith(name, 'c2'):
            mat_config['c2'] = {'file': abs_mat_file}
            mat_config['c_children_name_arr'].append({'name': re.sub('^c2', '', name), "sort": 2})
        elif str.startswith(name, 'c'):
            mat_config['c'] = {"file": abs_mat_file}
            mat_config['c_children_name_arr'].append({'name': re.sub('^c', '', name), "sort": -1})


    final_full_height = full_height
    has_c0 = True
    has_c2 = True
    # 没有c0子菜时, 总高度 - (2 * c_children_radius + 30)
    if ('c0' not in mat_config) and ('c1' not in mat_config):
        has_c0 = False
        has_c2 = False
        final_full_height -= (2 * c_children_radius + 30)
    # 没有c2子菜时, 总高度 - 2 * c_child_radius
    elif 'c2' not in mat_config:
        has_c2 = False
        final_full_height -= (2 * c_children_radius)

    to_img = Image.new('RGBA', (full_width, final_full_height))
    draw = ImageDraw.Draw(to_img)

    print('正在生成%s' % (menu_name))
    # print('%s menu_mat_config %s' %(menu_name, mat_config))



    # for mat_file in os.listdir(full_menu_dir):
    #     [name, ext] = path.splitext(mat_file)
    #     print(name, ext)

    # 绘制背景
    draw.rectangle((0, 0, full_width, full_height), 'white')

    # 标题绘制, top_0-160_mid
    # 标题字体
    font_title = ImageFont.truetype('SourceHanSerifCN-Bold', 48) # 不写.ttf后缀会自动搜索非.ttf字体
    # 其他字体
    font_normal = ImageFont.truetype('SourceHanSansCN-Light', 24)
    text_color_normal = '#333'
    [line_width_title, line_height_title] = draw.textsize(menu_name, font=font_title)
    # 注意坑, 这里的align只相对字体所占最大宽度定位居中, 不相对画布居中
    draw.text(((full_width - line_width_title) / 2, (160 - line_height_title - 10) / 2), menu_name, font=font_title, fill=text_color_normal, align="center")

    # 主菜绘制, top_160
    main_img = Image.open(mat_config['main']['file'])
    adjusted_main_img = main_img.resize((full_width, 450), Image.BILINEAR) # resize生成副本, 不改变原图片
    # print('[debugger] main_img size', adjusted_main_img.size)
    to_img.paste(adjusted_main_img, (0, 160))

    # 描述文案绘制, top_650
    fill_color_desc = '#333'
    desc = ''
    with open(mat_config['desc']['file'], 'r') as descFile:
        desc = descFile.read()
    # 分行
    [line_width_desc, line_height_desc] = draw.textsize(desc, font=font_normal, spacing=desc_spacing)
    lines_desc = line_width_desc / (full_width - desc_padding_left * 2 + 6) # 最后的减为调整: 未能领悟pillow是如何计算行宽

    desc_arr = partition(desc, int(len(desc) / lines_desc))
    # 最后一个标点为， 。时， 放在上一排
    lens_desc_arr = len(desc_arr)
    last_desc_arr_item = desc_arr[lens_desc_arr - 1]
    last_second_desc_arr_item = desc_arr[lens_desc_arr - 2]

    lens_last_desc_arr_item = len(last_desc_arr_item)
    last_item = last_desc_arr_item[lens_last_desc_arr_item - 1]
    if (last_item == '，' or last_item  == '。') and (lens_last_desc_arr_item == 1):
        last_second_desc_arr_item.append(last_item)
        del desc_arr[lens_desc_arr - 1]

    final_lines_desc = len(desc_arr)
    desc_str_arr = map(lambda arr: ''.join(arr), desc_arr)
    processed_desc_str = '\n'.join(desc_str_arr)
    [line_width_processed_desc, line_height_processed_desc] = draw.textsize(processed_desc_str, font=font_normal)
    line_height_processed_desc = 68
    # print('[line_width_processed_desc, line_height_processed_desc]', [line_width_processed_desc, line_height_processed_desc])
    draw.multiline_text((28, 650), processed_desc_str, font=font_normal, fill=fill_color_desc, align="left", spacing=desc_spacing)

    # 子菜绘制
    ## 主子菜
    c_top = int(650 + line_height_processed_desc * int(lines_desc) - desc_spacing + 10);
    # print('final_lines_desc %i' % final_lines_desc)
    if final_lines_desc == 1:
        c_top += 70;
    elif final_lines_desc == 2:
        c_top += 40;
    elif final_lines_desc == 3:
        pass
    elif final_lines_desc == 4:
        c_top -= 20;
    elif final_lines_desc == 5:
        c_top -= 40;

    c0_top = int(c_top + 326)
    c1_top = int(c_top + c_radius * 2 + 30)
    c2_top = c0_top
    abs_c_border_path = path.join(image_dir, '../', c_border_path)
    abs_c_child_border_path = path.join(image_dir, '../', c_child_border_path)

    if 'c' in mat_config:

        # drawCircleAvatar(avatar, to_img)
        draw_circle(c_radius * 2, mat_config['c']['file'], to_img, (int(full_width / 2 - c_radius), c_top), border_path=c_border_path, outline_width = 4)

    # 子菜0-2 0_left 1_mid 2_right
    if 'c0' in mat_config:
        draw_circle(c_children_radius * 2, mat_config['c0']['file'], to_img, (int(full_width - c_children_radius * 2 - 30), c0_top),  border_path=c_child_border_path, outline_width = 2)
    if 'c1' in mat_config:
        draw_circle(c_children_radius * 2, mat_config['c1']['file'], to_img, (42, c0_top), border_path=c_child_border_path, outline_width = 2)
    if 'c2' in mat_config:
        draw_circle(c_children_radius * 2, mat_config['c2']['file'], to_img, (int(full_width / 2 - c_children_radius), c1_top), border_path=c_child_border_path, outline_width = 2)


    # 底部品名 配料表
    foot_desc_1_title = '品名'
    foot_desc_1_text = menu_name
    foot_desc_2_title = '配料表'
    foot_desc_2_text  = ' '.join(map(lambda c_child: c_child['name'], sorted(mat_config['c_children_name_arr'], key=lambda item: item['sort'])))

    foot_desc_line_1_top = c_top + c_radius * 2 +  (30 if has_c0 else 0) + ((c_children_radius * 2) if has_c2 else 0) + 60
    for i in range(3):
        y = foot_desc_line_1_top + 38 * i
        draw.line((28, y, full_width - 28 * 2, y), '#f4efea', 1)



    font_foot_desc = ImageFont.truetype('SourceHanSansCN-Light', 22)
    text_color_desc_title = '#808080'
    foot_desc_line_margin_top = 8
    draw.text((28, foot_desc_line_1_top + foot_desc_line_margin_top), foot_desc_1_title, font=font_foot_desc, fill=text_color_desc_title, align="center")
    draw.text((126, foot_desc_line_1_top + foot_desc_line_margin_top), foot_desc_1_text, font=font_foot_desc, fill=text_color_normal, align="center")
    draw.text((28, foot_desc_line_1_top + foot_desc_line_margin_top + 38), foot_desc_2_title, font=font_foot_desc, fill=text_color_desc_title, align="center")
    draw.text((126, foot_desc_line_1_top + foot_desc_line_margin_top + 38), foot_desc_2_text, font=font_foot_desc, fill=text_color_normal, align="center")



    # toImg.show()
    to_img.save(path.join(image_dir, '../output/' + menu_name) + '.png')


'''
目前最好的版本, 但有点复杂
改图片颜色改outline_color即可
'''
def draw_circle(w, path, to_img, to_xy, border_path, outline_width = 0):
    (x, y) = (0, 0)
    ima = Image.open(path).convert("RGBA")

    ima = ima.resize((w, w), Image.ANTIALIAS)

    circle = Image.new('L', (w, w), 0)

    draw = ImageDraw.Draw(circle)

    outline_width = outline_width - 0.5 # 让里圆变大, 锯齿藏在外环下
    w_minus_outline_width = w - outline_width
    # mask内圆
    draw.ellipse((outline_width, outline_width, w_minus_outline_width, w_minus_outline_width), fill=255)

    # 外圆环
    mask_outline = Image.open(border_path).convert("RGBA")
    mask_outline.resize((w, w), Image.ANTIALIAS)



    # mask外环
    # draw.ellipse((0, 0) + (w, w), fill=None, outline=outline_color, width=outline_width)

    alpha = Image.new('L', (w, w), 255)

    # alpha.paste(mask_outline, (0, 0))
    alpha.paste(circle, (0, 0))
    #
    ima.putalpha(alpha)
    to_img.paste(ima, to_xy, ima)
    to_img.paste(mask_outline, to_xy, mask_outline)
    # ima.save('test_circle.png')

success_list = []
fail_list = []

def ensure_output_dir():
    output_name = 'output'
    if path.exists(output_name) and path.isdir(output_name):
        pass
    else:
        os.mkdir(output_name)

def read_materials_and_draw_menus(image_dir, menu_names = None, retry_fail = False):
    menu_name_arr = []
    if menu_names != None and isinstance(menu_names, list):
        menu_name_arr = menu_names
    else:
        menu_name_arr = os.listdir(image_dir)

    for menu_name in menu_name_arr:
        full_menu_dir = path.join(image_dir, menu_name)
        if path.isdir(full_menu_dir):
            try:
                gen_menu(image_dir, menu_name)
                success_list.append(menu_name)
            except Exception as e:
                print('发生错误: ', e)
                fail_list.append(menu_name)
            finally:
                # encoding='utf-8' + ensure_ascii=False: 以解决中文编码问题
                success_file = './retry-success.json' if retry_fail else './success.json'
                with open(success_file, 'w', encoding='utf-8') as success_f:
                    json.dump(success_list, success_f, ensure_ascii=False)

                if len(fail_list) > 0:
                    fail_msg = 'retry-fail部分菜生成失败, 参见retry-fail.json' if retry_fail  else '部分菜生成失败, 参见fail.json'
                    print(fail_msg)

                    fail_file = './retry-file.json' if retry_fail else './fail.json'
                    with open(fail_file, 'w', encoding='utf-8') as fail_f:
                        json.dump(fail_list, fail_f, ensure_ascii=False)






def gen(menu_names = None, retry_fail = False):
    ensure_output_dir()
    read_materials_and_draw_menus(path.join(curDir, 'images'), menu_names, retry_fail = retry_fail)

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == '--retry-fail':
        with open('./fail.json', 'r', encoding='utf-8') as fail_f:
            menu_names = json.load(fail_f)
            gen(menu_names, retry_fail = True)
    else:
        gen()

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


'''
# 简单能理解版本_todo: 边缘不圆滑 im.resize不管用
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


