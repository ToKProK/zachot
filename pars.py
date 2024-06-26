from selenium import webdriver
import time, requests, img2pdf, os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
from glob import glob



my_list = []
path_list = []
count_chapters = 0
nomer_glavi = 1
title_name = ""
arthist = ""
time_pause = 2
def parse_manga(link, path=None):
    try:
        global nomer_glavi
        nomer_glavi = 1
        #Настройка юзер агента
        options_Fire = webdriver.FirefoxOptions()
        #Делаем браузер невимым
        options_Fire.add_argument("-headless")#https://ru.stackoverflow.com/questions/1330358/%D0%9D%D0%B5-%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%B0%D0%B5%D1%82-headless-firefox-selenium
        #Получение драйвера и вставка юзер агента
        try:
            driver = webdriver.Firefox(options=options_Fire)#Если не получилость пытаемся запустить драйвер firefox
        except:
            print("Не удалось запустить дравйвер Firefox")

        #Растягиваем окно во всю ширину.
        driver.maximize_window()
        #Переход по ссылке
        driver.get(link)
        time.sleep(time_pause)

        #Попытка получить название
        title_name = driver.find_element(By.CLASS_NAME, "media-name__main").text

        #Нажимаю на кнопку начать читать
        driver.find_element(By.LINK_TEXT, "Начать читать").click()
        time.sleep(0.2)
        #Кликаем по вкладке глав
        driver.find_element(By.XPATH, "//div[@data-reader-modal='chapters']").click()
        chapters = driver.find_elements(By.CLASS_NAME, "menu__item")
        count_chapters = (len(chapters))
        print(f"Количесвто глав = {count_chapters}")
        driver.find_element(By.CLASS_NAME, "popup_side").click()


        #Главы
        for i in range(0, count_chapters):
            #Смотрим количество страниц
            pages = driver.find_elements(By.XPATH, "//option")
            count_page = (len(pages))
            print(f"В данной главе {count_page} стр.")
            #Очищаем списки
            my_list.clear()
            path_list.clear()
            for b in range(1, count_page + 1): # Цикл по перебору всех страниц в главе
                for trying in range(3): # Цикл по попытке сбора информации (иногда из-за того, что страница не загрузилась выдаётся ошибка)
                    try:
                        time.sleep(0.2)
                        image = driver.find_element(By.XPATH, "//div[@class='reader-view__wrap']/img")
                        img = image.get_attribute("src")
                        print("Link + " + img)
                        time.sleep(0.1)#если убрать эту паузу, то возникнет ошибка. Ссылка на решение проблемы - https://stackoverflow.com/questions/23557471/clicking-on-image-results-in-an-error-element-is-not-clickable-at-point-97-42
                        image.click()
                        time.sleep(0.2)
                        my_list.append(img)
                        break
                    except:
                        print(f'{trying} попытка провалена')
            
            number_page = 0
            Full_path_dir = create_directory(path=path, title_name=title_name)# Создаём директорию и получаем её путь
            for img_url in my_list:
                req = requests.get(url=img_url)
                response = req.content
                number_page+=1
                with open(f"{Full_path_dir}/{number_page}.png", "wb") as file: # Загружаем все изображения в созданный каталог
                    file.write(response)
                    path_list.append(f"{Full_path_dir}/{number_page}.png")
                    print(f"Download {number_page} page")
            print(f"Глава №{count_chapters} успешно скачана")
            #Конвертируем картинки в pdf файл.
            convert(title_name=title_name, path=Full_path_dir)
            #Удаляем все картинки
            Del_image(path=Full_path_dir)
        print("Все главы скачанны")
        return True

    except Exception as ex:
        print(ex)
        return False
    finally:
        driver.close()
        driver.quit()

def create_directory(path, title_name):
    if path != None and path != "" and path != 'None': # Тут создаётся папка по выбранному пользователем пути, куда бует все складироваться
        Full_path_dir = os.path.join(path, title_name)# Путь для создания папки, в выбранном каталоге
    else: # Если пользователь не указал путь
        work_dir = os.getcwd() # Узнаём  путь проекта
        Full_path_dir = os.path.join(work_dir, title_name)# Путь для создания папки, в каталоге проекта
    
    if os.path.isdir(Full_path_dir) != True:
        os.mkdir(Full_path_dir)# Создаём директорию в которй будем работать
        print("Папка созданна")
    else:
        print("Папка уже была")
    
    return Full_path_dir

def convert(title_name, path):
    global nomer_glavi
    print(path_list)
    #Проверяем файл на наличие запрещённых символов
    title_name = Check_file_name(title_name)
    # Создаём пдф файл главы
    with open(f"{path}/{title_name}, {nomer_glavi}.pdf", "wb") as f:
        f.write(img2pdf.convert(path_list))
    print(f"Конвертация {nomer_glavi} главы прошла успешно!")
    nomer_glavi = nomer_glavi + 1

def Del_image(path): # Удаляем все скачанные картинки в папке, после конвертации их в пдф
    pattern = '*.png'
    pattern_path = os.path.join(path, pattern)# Шаблон по которому будут удалятся картинки
    image_path = glob(pattern_path)#Использую библиотеку glob
    for file in image_path:
        os.remove(file)
def Check_file_name(file_name): # Замена символов, которые не могут быть в название файлов
    char_remov = ['*', '|', "\\", ':', '"', '<', '>', '?','/' ]
    for char in char_remov:
        file_name = file_name.replace(char, "#")
    return file_name

def main():
    link = ""
    parse_manga(link=link)

if __name__=="__main__":
    main()