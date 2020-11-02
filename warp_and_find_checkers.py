import os
import cv2
import numpy as np
import fire
import json

images = {}

def get_circles(im):
    cim = im
    if len(im.shape)==3:
        cim = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    circles = cv2.HoughCircles(cim, cv2.HOUGH_GRADIENT, 2.7, 60, minRadius=60, maxRadius=65)
    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        # draw the outer circle
        cv2.circle(im, (i[0], i[1]), i[2], (0,255,0), 2)
        # draw the center of the circle
        cv2.circle(im, (i[0],i[1]), 2, (0,0,255), 3)
    return im, circles


def outside_board(point, board):
    if point[0] < board[0][0] or point[0] > board[1][0]:
        return True
    if point[1] < board[0][1] or point[1] > board[3][1]:
        return True
    return False

def on_bar(point, bar_ini, bar_end):
    if point[0] >= bar_ini and point[0] <= bar_end:
        return True
    return False

def get_pip(checker, board, bar_size, bar_ini, bar_end):
    board_width = board[1][0] - board[0][0]
    half_board_width = int(board_width/2 - bar_size/2)
    pip_width = int(half_board_width/6)
    if checker[0] > 1000:
        # right
        checker_n_board_pos = checker[0] - 1000 - int(bar_size/2)
        checker_pos = int(checker_n_board_pos/pip_width)
        ret = checker_pos + 6
    else:
        # left
        checker_n_board_pos = checker[0] - board[0][0]
        checker_pos = int(checker_n_board_pos/pip_width)
        ret = checker_pos
    return ret

def get_checkers(info, board, circles):
    top_checkers = [0]*12
    bottom_checkers = [0]*12
    bar_size = info["bar_width_to_checker_width"]*65
    bar_ini_x = int(1000 - bar_size/2 - 5)
    bar_end_x = int(1000 + bar_size/2 + 5)
    for checker in circles:
        if outside_board(checker, board):
            continue
        if on_bar(checker, bar_ini_x, bar_end_x):
            continue
        if checker[1] > 1000:
            bottom_checkers[get_pip(checker, board, bar_size, bar_ini_x, bar_end_x)] += 1
            continue
        top_checkers[get_pip(checker, board, bar_size, bar_ini_x, bar_end_x)] += 1
    return {'top': top_checkers, 'bottom': bottom_checkers}


def run(input_folder, output_folder):
    for fn in os.listdir(input_folder):
        fn_parts = fn.split('.')
        im_name = fn_parts[0]
        if im_name not in images:
            images[im_name] = {'im': None, 'json': None, 'checkers': None}
        if 'json' in fn_parts:
            with open(os.path.join(input_folder, fn)) as json_file:
                images[im_name]['json'] = json.load(json_file)['canonical_board']
        elif 'jpg' in fn_parts or 'jpeg' in fn_parts or 'png' in fn_parts:
            images[im_name]['im'] = cv2.imread(os.path.join(input_folder, fn))
            images[im_name]['ext'] = '.' + fn_parts[1]
    
    os.makedirs(output_folder, exist_ok=True)
    for image in images:
        board_width_to_board_height = images[image]['json']['board_width_to_board_height']
        x_coord = int(board_width_to_board_height*200)
        dest_points = [[x_coord, 200], [2000-x_coord, 200], [2000-x_coord, 1800], [x_coord, 1800]]
        h, status = cv2.findHomography(np.array(images[image]['json']['tl_tr_br_bl']), np.array(dest_points))
        images[image]['im'] = cv2.warpPerspective(images[image]['im'], h, (int(2000*board_width_to_board_height), 2000))
        images[image]['im'], circles = get_circles(images[image]['im'])
        images[image]['checkers'] = get_checkers(images[image]['json'], dest_points, circles[0])
        with open(os.path.join(output_folder, image + images[image]['ext'] + '.checkers.json'), 'w') as outfile:
            json.dump(images[image]['checkers'], outfile)
        images[image]['im'] = cv2.drawContours(images[image]['im'], np.array([dest_points]), -1, (0, 255, 0), 3) 
        images[image]['im'] = cv2.resize(images[image]['im'], (1000, 1000))
        cv2.imwrite(os.path.join(output_folder, image + '.visual_feedback.jpg'), images[image]['im'])


if __name__ == "__main__":
    fire.Fire(run)
