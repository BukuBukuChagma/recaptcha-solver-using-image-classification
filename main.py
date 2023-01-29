from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os, time, requests, cv2, glob
from inference import inference


options = webdriver.ChromeOptions()
options.add_argument("--log-level=3")
options.binary_location = "C:\\Program Files\\Google\\Chrome Beta\\Application\\chrome.exe"
options.add_argument("user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.29 Safari/537.36")
bot = webdriver.Chrome(service=Service("chromedriver.exe"), options=options)
captcha_counts = 0
while(1):
    skip_this = False
    bot.get("https://www.google.com/recaptcha/api2/demo")
    wait = WebDriverWait(bot, 10)
    bot.find_element(By.ID, "recaptcha-demo").click()
    wait.until(EC.frame_to_be_available_and_switch_to_it(bot.find_element(By.XPATH, "//iframe[@title='recaptcha challenge expires in two minutes']")))
    time.sleep(3)

    try:
        captcha_class = bot.find_element(By.XPATH, "//div[@id='rc-imageselect']/div[2]/div[1]/div[1]/div[1]/strong").text
    except:
        captcha_class = bot.find_element(By.XPATH, "//div[@id='rc-imageselect']/div[2]/div[1]/div[1]/div[2]/strong").text
    rows = bot.find_elements(By.XPATH, "//div[@id='rc-imageselect-target']/table/tbody/tr")
    for row in range(len(rows)):
        cols = bot.find_elements(By.XPATH, f"//div[@id='rc-imageselect-target']/table/tbody/tr[{row+1}]/td")
        for col in range(len(cols)):
            total_images = len(rows) * len(cols)
            img = bot.find_element(By.XPATH, f"//div[@id='rc-imageselect-target']/table/tbody/tr[{row+1}]/td[{col+1}]/div/div[1]/img").get_attribute("src")
            img_data = requests.get(img).content
            with open(f"images/image{total_images}.jpg", 'wb') as handler:
                handler.write(img_data)
            break
        break
    time.sleep(100)
    if total_images == 9:
        divider = 3
    elif total_images == 16:
        #divider = 4
        skip_this=True

    if not skip_this:
        img = cv2.imread(f'./images/image{total_images}.jpg')

        x_factor, y_factor = img.shape[0]//divider , img.shape[1]//divider

        img_save = 0
        for x in range(len(cols)):
            for y in range(len(rows)):
                cropped_image = img[x_factor*x:x_factor*(x+1), y_factor*y:y_factor*(y+1)]
                cv2.imwrite(f"./cropped_images/image{img_save}.jpg", cropped_image)
                img_save+=1

        files = glob.glob('./images/*')
        for f in files:
            os.remove(f)

        images = os.listdir("./cropped_images/")
        class_list = list()
        for image in images:
            class_name, conf = inference(f"./cropped_images/{image}")
            class_list.append(class_name)


        print(captcha_class)
        print(class_list)
        count = 0
        rows = bot.find_elements(By.XPATH, "//div[@id='rc-imageselect-target']/table/tbody/tr")
        for row in range(len(rows)):
            cols = bot.find_elements(By.XPATH, f"//div[@id='rc-imageselect-target']/table/tbody/tr[{row+1}]/td")
            for col in range(len(cols)):
                img = bot.find_element(By.XPATH, f"//div[@id='rc-imageselect-target']/table/tbody/tr[{row+1}]/td[{col+1}]")
                for i in range(2):
                    if class_list[row+col][i].find(captcha_class) != -1:
                        img.click()
                        count+=1
                        time.sleep(4)

    bot.save_screenshot(f"./results/{captcha_counts}.png")
    bot.quit()
    files = glob.glob('./cropped_images/*')
    for f in files:
        os.remove(f)

    # cont = True
    # skip = True
    # try:
    #     bot.find_element(By.XPATH, "//*[contains(text(), 'Skip')]")
    # except:
    #     skip = False

    # bot.find_element(By.XPATH, "//button[@id='recaptcha-verify-button']").click()

    # if not skip:
    #     try:
    #         bot.find_element(By.XPATH,"//*[contains(text(), 'Please select all matching images.')]")
    #     except:
    #         try:
    #             bot.find_element(By.XPATH, "//*[contains(text(), 'Please also check the new images.')]")
    #         except:
    #             try:
    #                 bot.find_element(By.XPATH,"//*[contains(text(), 'Please try again')]")
    #             except:
    #                 cont = False
    # if not cont:
    #     break

    time.sleep(5)





