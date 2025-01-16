import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw


class DrawingApp:
    """
    Приложение для рисования с возможностью сохранения в формате PNG.

    Позволяет пользователю рисовать на холсте, выбирать цвет и размер кисти,
    очищать холст, использовать ластик и сохранять рисунок в файл.
    Также добавлена пипетка для выбора цвета с холста.

    Атрибуты:
        root (tk.Tk): Главное окно приложения.
        image (PIL.Image.Image): Изображение, на котором происходит рисование.
        draw (PIL.ImageDraw.Draw): Объект для рисования на изображении.
        canvas (tk.Canvas): Холст Tkinter, на котором отображается рисунок.
        last_x (int): Координата X предыдущей точки.
        last_y (int): Координата Y предыдущей точки.
        pen_color (str): Текущий цвет кисти.
        brush_size_var (tk.IntVar): Переменная Tkinter, хранящая текущий размер кисти.
        brush_size_scale (tk.Scale): Шкала для выбора размера кисти.
        selected_size (tk.StringVar): Переменная Tkinter, хранящая текущий размер кисти (строковое представление).
        brush_size_menu (tk.OptionMenu): Выпадающий список для выбора размера кисти.
        eraser_mode (bool): Флаг, указывающий, активен ли режим ластика.
        previous_color (str): Предыдущий цвет кисти (до активации ластика).
        mode_label (tk.Label): Метка, отображающая текущий режим (Кисть/Ластик).
        eraser_button (tk.Button): Кнопка включения/выключения ластика.
        eraser_indicator (tk.Canvas):  Круглый индикатор состояния ластика.
        brush_color_indicator (tk.Canvas): Круглый индикатор цвета кисти.
    """

    def __init__(self, root):
        """
        Инициализирует приложение DrawingApp.

        """
        self.root = root
        self.root.title("Рисовалка с сохранением в PNG")

        self.image = Image.new("RGB", (630, 400), "white")  # Создаем новое изображение PIL белого цвета
        self.draw = ImageDraw.Draw(self.image)  # Создаем объект ImageDraw для рисования на изображении

        self.canvas = tk.Canvas(root, width=630, height=400, bg='white')  # Создаем холст Tkinter
        self.canvas.pack()  # Размещаем холст в окне

        self.setup_ui()  # Настраиваем пользовательский интерфейс

        self.last_x, self.last_y = None, None  # Инициал-ем координаты предыдущей точки (None, None в начале рисования)
        self.pen_color = 'black'  # Инициализируем цвет пера (по умолчанию черный)
        self.eraser_mode = False  # Инициализируем флаг режима ластика (по умолчанию выключен)
        self.previous_color = self.pen_color  # Инициализируем предыдущий цвет

        self.canvas.bind('<B1-Motion>', self.paint)  # Привязываем событие движения мыши с зажатой левой кнопкой к
        # методу paint
        self.canvas.bind('<ButtonRelease-1>', self.reset)  # Привязываем событие отпускания левой кнопки мыши к
        # методу reset
        self.canvas.bind('<Button-3>', self.pick_color)  # Привязываем правую кнопку мыши к pick_color

    def setup_ui(self):
        """
        Настраивает пользовательский интерфейс приложения.

        Создает кнопки, шкалы, выпадающий список для управления рисованием.
        """
        control_frame = tk.Frame(self.root)  # Создаем фрейм для элементов управления
        control_frame.pack(fill=tk.X)  # Размещаем фрейм в окне, растягивая по горизонтали

        clear_button = tk.Button(control_frame, text="Очистить", command=self.clear_canvas)  # Создаем кнопку "Очистить"
        clear_button.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем кнопку слева с отступами

        color_button = tk.Button(control_frame, text="Выбрать цвет",
                                 command=self.choose_color)  # Создаем кнопку "Выбрать цвет"
        color_button.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем кнопку слева с отступами

        save_button = tk.Button(control_frame, text="Сохранить", command=self.save_image)  # Создаем кнопку "Сохранить"
        save_button.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем кнопку слева с отступами

        # Рамка для кнопки "Ластик", индикатора и метки отображения режима
        # eraser_frame = tk.Frame(control_frame)
        eraser_frame = tk.LabelFrame(control_frame, text="Выбор режима", height=50)
        eraser_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)  # Размещаем рамку слева с отступами и заполнением
        # по вертикали

        # Добавляем кнопку "Ластик"
        self.eraser_button = tk.Button(eraser_frame, text="Ластик", command=self.toggle_eraser)
        self.eraser_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Добавляем индикатор состояния ластика
        self.eraser_indicator = tk.Canvas(eraser_frame, width=14, height=14, highlightthickness=0)
        self.eraser_indicator.pack(side=tk.LEFT, padx=2)
        self.eraser_indicator.create_oval(2, 2, 12, 12, fill='gray', outline='gray', tags="indicator")  # Серый кружок
        # по умолчанию

        # Рамка для выбора размера кисти
        brush_size_frame = tk.LabelFrame(control_frame, text="Выбор размера кисти", height=50)  # Создаем LabelFrame
        # (рамка с заголовком)
        brush_size_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)  # Размещаем рамку слева с отступами и
        # заполнением по вертикали

        self.brush_size_var = tk.IntVar(value=5)  # Создаем переменную Tkinter для хранения размера кисти
        # (начальное значение 5)

        # Создаем шкалу для выбора размера кисти и связываем с переменной brush_size_var
        self.brush_size_scale = tk.Scale(brush_size_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                         variable=self.brush_size_var, command=self.update_menu_from_scale)
        self.brush_size_scale.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем шкалу внутри рамки

        sizes = [1, 2, 5, 10]  # Список предопределенных размеров кисти
        self.selected_size = tk.StringVar(value=str(sizes[2]))  # Создаем StringVar для хранения выбранного размера
        # (строковое представление, начальное значение "5")

        # Создаем выпадающий список для выбора размера кисти
        self.brush_size_menu = tk.OptionMenu(brush_size_frame, self.selected_size, *sizes,
                                             command=self.update_scale_from_menu)
        self.brush_size_menu.config(width=3)  # Устанавливаем ширину выпадающего списка
        self.brush_size_menu.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем меню внутри рамки

        # Добавляем метку для отображения текущего режима
        # self.mode_label = tk.Label(control_frame, text="Режим: Кисть")  # Начальное значение - "Кисть"
        # self.mode_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.mode_label = tk.Label(eraser_frame, text="Режим: Кисть")  # Привязываем ее к ластику и индикатору
        self.mode_label.pack(side=tk.LEFT, padx=5, pady=5)

        # Добавляем индикатор выбранного цвета кисти
        self.brush_color_indicator = tk.Canvas(eraser_frame, width=14, height=14, highlightthickness=0)
        self.brush_color_indicator.pack(side=tk.LEFT, padx=2)
        self.brush_color_indicator.create_oval(2, 2, 12, 12, fill='black', outline='black', tags="indicator_brush")
        # Изначально черный цвет

        # Добавляем горячие клавиши
        self.root.bind('<Control-s>', self.save_image)  # Привязка Ctrl+s к функции сохранения изображения
        self.root.bind('<Control-c>', self.choose_color)  # Привязка Ctrl+c к функции выбора цвета

    def update_menu_from_scale(self, value):
        """
        Обновляет значение в выпадающем списке при изменении значения шкалы.

        Args:
            value (str): Новое значение размера кисти (строковое представление).
        """
        self.selected_size.set(value)  # Устанавливаем новое значение в StringVar, связанной с меню

    def update_scale_from_menu(self, value):
        """
        Обновляет значение шкалы при выборе значения из выпадающего списка.

        Args:
            value (str): Новое значение размера кисти (строковое представление).
        """
        self.brush_size_var.set(int(value))  # Устанавливаем новое значение в IntVar, связанной со шкалой

    def paint(self, event):
        """
        Рисует линию на холсте и на изображении PIL при движении мыши.

        Args:
            event (tk.Event): Объект события Tkinter, содержащий информацию о событии мыши.
        """
        if self.last_x and self.last_y:  # Проверяем, были ли установлены предыдущие координаты
            # Рисуем линию на холсте Tkinter
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                    width=self.brush_size_var.get(),  # Используем текущий размер кисти
                                    fill=self.pen_color,
                                    capstyle=tk.ROUND, smooth=tk.TRUE)
            # Рисуем линию на изображении PIL
            self.draw.line([self.last_x, self.last_y, event.x, event.y], fill=self.pen_color,
                           width=self.brush_size_var.get())  # Используем текущий размер кисти

        self.last_x = event.x  # Обновляем координаты предыдущей точки
        self.last_y = event.y

    def reset(self, event):
        """
        Сбрасывает координаты предыдущей точки.

        Args:
            event (tk.Event): Объект события Tkinter (не используется, но нужен для корректной работы привязки).
        """
        self.last_x, self.last_y = None, None  # Сбрасываем координаты

    def clear_canvas(self):
        """
        Очищает холст и создает новое белое изображение.
        """
        self.canvas.delete("all")  # Очищаем холст Tkinter
        self.image = Image.new("RGB", (630, 400), "white")  # Создаем новое изображение PIL
        self.draw = ImageDraw.Draw(self.image)  # Создаем новый объект ImageDraw для нового изображения

    def choose_color(self, event=None):  # event=None для возможности вызова функции горячей клавишей
        """
        Открывает диалог выбора цвета и обновляет текущий цвет кисти.
        Функция принимает аргумент event, хотя явно его не использует, для совместимости с bind.
        """
        chosen_color = colorchooser.askcolor(color=self.pen_color)[1]  # Открываем диалог выбора цвета
        if chosen_color:  # Проверяем, был ли выбран цвет
            self.pen_color = chosen_color  # Обновляем цвет кисти
            self.previous_color = self.pen_color  # Обновляем предыдущий цвет, если не в режиме ластика
            self.eraser_mode = False  # Выключаем режим ластика
            self.update_mode_label()  # Обновляем метку режима
            self.update_eraser_indicator()  # Обновляем индикатор ластика
            self.update_brush_color_indicator()  # Обновляем индикатор цвета кисти

    def save_image(self, event=None):  # event=None для возможности вызова функции горячей клавишей
        """
        Открывает диалог сохранения файла и сохраняет изображение в формате PNG.
        Функция принимает аргумент event, хотя явно его не использует, для совместимости с bind.
        """
        file_path = filedialog.asksaveasfilename(defaultextension='.png',  # Задаем расширение по умолчанию
                                                 filetypes=[('PNG files', '*.png')],  # Указываем типы файлов
                                                 title="Сохранить изображение как")
        if file_path:  # Проверяем, был ли выбран путь к файлу
            self.image.save(file_path)  # Сохраняем изображение
            messagebox.showinfo("Информация", "Изображение успешно сохранено!")  # Показываем сообщение

    def toggle_eraser(self):
        """
        Переключает режим ластика.
        """
        self.eraser_mode = not self.eraser_mode  # Инвертируем флаг режима ластика
        if self.eraser_mode:
            # Если режим ластика включен, сохраняем текущий цвет и устанавливаем цвет ластика (белый)
            self.previous_color = self.pen_color
            self.pen_color = "white"
        else:
            # Если режим ластика выключен, восстанавливаем предыдущий цвет
            self.pen_color = self.previous_color
        self.update_mode_label()  # Обновляем метку
        self.update_eraser_indicator()  # Обновляем индикатор
        self.update_brush_color_indicator()  # Обновляем индикатор цвета кисти

    def update_mode_label(self):
        """
        Обновляет текст метки режима в зависимости от значения self.eraser_mode.
        """
        if self.eraser_mode:
            self.mode_label.config(text="Режим: Ластик")
        else:
            self.mode_label.config(text="Режим: Кисть")

    def update_eraser_indicator(self):
        """Обновляет цвет индикатора ластика."""
        if self.eraser_mode:
            self.eraser_indicator.itemconfig("indicator", fill="white", outline="black")  # Белый, если включен
        else:
            self.eraser_indicator.itemconfig("indicator", fill="gray", outline="gray")  # Серый, если выключен

    def pick_color(self, event):
        """
        Выбирает цвет пикселя на холсте под курсором мыши (правая кнопка).

        Args:
            event (tk.Event): Объект события, содержащий координаты щелчка мыши.
        """
        x, y = event.x, event.y  # Получаем координаты клика
        try:
            # Пытаемся получить цвет пикселя из изображения
            rgb = self.image.getpixel((x, y))
            # Преобразуем RGB в шестнадцатеричный формат
            hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)
            self.pen_color = hex_color  # Устанавливаем текущий цвет пера
            self.previous_color = self.pen_color  # Обновляем предыдущий цвет
            self.eraser_mode = False  # Переключаем режим на "Кисть", если был включен ластик
            self.update_mode_label()  # обновляем режим
            self.update_eraser_indicator()  # Обновляем индикатор ластика
            self.update_brush_color_indicator()  # Обновляем индикатор цвета кисти

        except IndexError:
            # Обрабатываем случай, когда клик был за пределами изображения
            messagebox.showwarning("Внимание", "Вы кликнули за пределами холста!")

    def update_brush_color_indicator(self):
        """Обновляет цвет индикатора цвета кисти."""
        if self.eraser_mode:
            # Если ластик включен, устанавливаем цвет индикатора в серый цвет
            self.brush_color_indicator.itemconfig("indicator_brush", fill='gray', outline='gray')
        else:
            # Иначе устанавливаем цвет индикатора в текущий цвет кисти
            self.brush_color_indicator.itemconfig("indicator_brush", fill=self.pen_color, outline=self.pen_color)


def main():
    """
    Создает главное окно приложения и запускает основной цикл обработки событий.
    """
    root = tk.Tk()  # Создаем главное окно
    app = DrawingApp(root)  # Создаем экземпляр приложения
    root.mainloop()  # Запускаем главный цикл обработки событий Tkinter


if __name__ == "__main__":
    main()
