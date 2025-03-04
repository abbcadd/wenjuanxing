from DrissionPage import ChromiumPage
import random
import time
from concurrent.futures import ThreadPoolExecutor  # 添加线程池支持
from DrissionPage import ChromiumOptions

def random_delay(min=0.05, max=0.3):
    time.sleep(random.uniform(min, max))

def handle_single_choice(page, all_questions):
    """优化单选题处理"""
    options_single_list = all_questions.get('3', [])
    print(f'发现单选题数量：{len(options_single_list)}')
    for question in options_single_list:
        try:
            options = question.eles('@class=ui-radio', timeout=0.1)  # 降低超时时间
            if options:
                random.choice(options).click()  
                random_delay(0.02, 0.1)  # 缩短延迟范围
        except Exception as e:
            print(f'单选题处理异常：{str(e)}')

def handle_multiple_choice(page, all_questions, other_responses=None):
    """优化多选题处理，包括‘其他’选项"""
    if other_responses is None:
        other_responses = ["冥想和放松练习", "运动", "规律作息", "环境优化", "无法确定"]
    
    options_multi_list = all_questions.get('4', [])
    print(f'发现多选题数量：{len(options_multi_list)}')
    
    for question in options_multi_list:
        try:
            checkboxes = question.eles('@class=ui-checkbox', timeout=0.1)
            if checkboxes:
                k = random.randint(1, len(checkboxes))
                selected = random.sample(checkboxes, k)
                for cb in selected:
                    cb.click()
                    if "其他" in cb.text.lower():
                        input_field = question.ele('xpath:.//input[@type="text"]', timeout=0.1)
                        if input_field:
                            input_field.input(random.choice(other_responses))  # JS输入更快
                    random_delay(0.02, 0.1)
        except Exception as e:
            print(f'多选题处理异常：{str(e)}')

def handle_rating_scale(page, all_questions, probabilities=None):
    """优化量表题处理"""
    if probabilities is None:
        probabilities = [0.2] * 5
    elif len(probabilities) != 5 or abs(sum(probabilities) - 1) > 0.01:
        raise ValueError("概率数组必须包含5个元素且和为1")
    
    options_table_list = all_questions.get('6', [])
    print(f'发现量表题数量：{len(options_table_list)}')
    
    for question in options_table_list:
        try:
            rows = question.eles('@tp=d', timeout=0.1)
            for row in rows:
                options = row.eles('@class=rate-off rate-offlarge', timeout=0.1)
                if options:
                    selected_index = random.choices(range(len(options)), weights=probabilities, k=1)[0]
                    options[selected_index].click()
                    random_delay(0.02, 0.1)
        except Exception as e:
            print(f'量表题处理异常：{str(e)}')

def handle_slider_matrix(page, all_questions, probabilities=None):
    """优化矩阵滑动题处理"""
    if probabilities is None:
        probabilities = [0.2] * 5
    elif len(probabilities) != 5 or abs(sum(probabilities) - 1) > 0.01:
        raise ValueError("概率数组必须包含5个元素且和为1")
    
    options_table_list_move = all_questions.get('9', [])
    print(f'发现矩阵滑动题数量：{len(options_table_list_move)}')
    
    for question in options_table_list_move:
        try:
            rows = question.eles('xpath://input[@class="ui-slider-input"]', timeout=0.1)
            for row in rows:
                score = random.choices([1, 2, 3, 4, 5], weights=probabilities, k=1)[0]
                row.input(score)
                random_delay(0.02, 0.1)
        except Exception as e:
            print(f'矩阵滑动题处理异常：{str(e)}')

def handle_stars(page, all_questions):
    """优化星标题处理"""
    stars = all_questions.get('5', [])
    print(f'发现星标题数量：{len(stars)}')
    for question in stars:
        try:
            options = question.eles('@class=td', timeout=0.1)
            if options:
                random.choice(options).click()
                random_delay(0.02, 0.1)
        except Exception as e:
            print(f'星标题处理异常：{str(e)}')

def process_question_types(page, all_questions):
    """并行处理所有题型"""
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.submit(handle_single_choice, page, all_questions)
        executor.submit(handle_multiple_choice, page, all_questions, ["冥想和放松练习", "运动", "规律作息", "环境优化", "无法确定"])
        executor.submit(handle_rating_scale, page, all_questions, [0.1, 0.2, 0.4, 0.2, 0.1])
        executor.submit(handle_slider_matrix, page, all_questions, [0.3, 0.25, 0.2, 0.15, 0.1])
        executor.submit(handle_stars, page, all_questions)


def main():
    # 代理池配置（请将所有IP放入此列表）
    proxy_pool = [
        '60.188.79.111:20199',
        # '60.188.78.8:20103',
        # '60.188.78.11:20021',
        # '60.188.78.7:20161',
        # 此处添加剩余代理IP...
        # '27.152.28.223:30176',
        # '60.188.78.8:20019'
    ]
    
    try:
        # 浏览器配置
        co = ChromiumOptions()
        co.set_address('36.6.144.46:8089')  # 保留原始地址设置
        proxy = random.choice(proxy_pool)
        co.set_proxy(f'http://{proxy}')  # 设置随机代理
        co.incognito()  # 无痕模式防止指纹追踪
        co.set_timeouts(20)  # 全局超时20秒

        # 创建浏览器实例
        driver = ChromiumPage(addr_or_opts=co)
        driver.clear_cache()

        # 页面操作
        page = driver
        page.get('https://www.wjx.cn/vm/rAKG1KW.aspx', retry=1, timeout=15)
        
        try:
            wait = page.ele('xpath://a[@class="layui-layer-btn0"]', timeout=1)
            wait.click()
        except:
            page.scroll.to_bottom()
            all_questions = {
                '3': page.eles('@type=3', timeout=1),
                '4': page.eles('@type=4', timeout=1),
                '5': page.eles('@type=5', timeout=1),
                '6': page.eles('@type=6', timeout=1),
                '9': page.eles('@type=9', timeout=1)
            }
            
            process_question_types(page, all_questions)
            
            # 提交操作
            page.ele('@id=ctlNext').click()
            random_delay(0.5, 1.5)  # 增加提交延迟
            page.refresh(ignore_cache=True)

        driver.quit()
        print(f'[成功] 代理 {proxy} 提交完成')
        return True
        
    except Exception as e:
        print(f'[失败] 代理 {proxy} 错误: {str(e)}')
        if 'driver' in locals():
            driver.quit()
        return False

if __name__ == '__main__':
    for _ in range(600):
        main()