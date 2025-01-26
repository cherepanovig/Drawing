import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, simpledialog
from PIL import Image, ImageDraw, ImageFont


class DrawingApp:
    """
    Приложение для рисования с возможностью сохранения в формате PNG и изменения размера холста.

    Позволяет пользователю рисовать на холсте, выбирать цвет и размер кисти,
    очищать холст, использовать ластик, сохранять рисунок в файл и изменять размер холста.
    Также добавлена пипетка для выбора цвета с холста. Есть возможность ввода текста и изменения фона изображения.

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
        mode_label_fg (str): Цвет текста метки режима (соответствует цвету кисти).
        text_mode (bool): Флаг, указывающий, включен ли режим добавления текста.
        entered_text (str): Текст, введённый пользователем при активации режима "Текст".
        text_size (int): Размер шрифта, который пользователь выбирает при вводе текста.

    """

    def __init__(self, root):
        """
        Инициализирует приложение DrawingApp.
        """
        self.root = root
        self.root.title("Рисовалка с сохранением в PNG")

        self.image = Image.new("RGB", (850, 500), "white")  # Создаем новое изображение PIL белого цвета
        self.draw = ImageDraw.Draw(self.image)  # Создаем объект ImageDraw для рисования на изображении

        self.canvas = tk.Canvas(root, width=850, height=500, bg='white')  # Создаем холст Tkinter
        self.canvas.pack()  # Размещаем холст в окне

        self.setup_ui()  # Настраиваем пользовательский интерфейс

        self.last_x, self.last_y = None, None  # Инициализируем координаты предыдущей точки (None, None в начале
        # рисования)
        self.pen_color = 'black'  # Инициализируем цвет пера (по умолчанию черный)
        self.eraser_mode = False  # Инициализируем флаг режима ластика (по умолчанию выключен)
        self.previous_color = self.pen_color  # Инициализируем предыдущий цвет
        self.mode_label_fg = "black"  # Инициализация цвета текста метки режима
        self.update_mode_label_color()  # Обновляем цвет текста метки режима

        self.text_mode = False  # Инициализируем флаг режима текста
        self.entered_text = None  # Инициализируем текст, введенный пользователем
        self.text_size = 12  # Размер шрифта по умолчанию

        self.canvas.bind('<B1-Motion>',
                         self.paint)  # Привязываем событие движения мыши с зажатой левой кнопкой к методу paint
        self.canvas.bind('<ButtonRelease-1>',
                         self.reset)  # Привязываем событие отпускания левой кнопки мыши к методу reset
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

        resize_button = tk.Button(control_frame, text="Изменить размер",
                                  command=self.resize_canvas)  # Создаем кнопку "Изменить размер"
        resize_button.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем кнопку слева с отступами

        change_bg_button = tk.Button(control_frame, text="Изменить фон",
                                     command=self.change_background)  # Создаем кнопку "Изменить фон"
        change_bg_button.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем кнопку слева с отступами

        text_button = tk.Button(control_frame, text="Текст", command=self.start_text_mode)  # Создаем кнопку "Текст"
        text_button.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем кнопку слева с отступами

        eraser_frame = tk.LabelFrame(control_frame, text="Выбор режима",
                                     height=50)  # Создаем рамку для элементов управления ластиком
        eraser_frame.pack(side=tk.LEFT, padx=5, pady=5,
                          fill=tk.Y)  # Размещаем рамку слева с отступами и заполнением по вертикали

        self.eraser_button = tk.Button(eraser_frame, text="Ластик",
                                       command=self.toggle_eraser)  # Создаем кнопку "Ластик"
        self.eraser_button.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем кнопку слева с отступами

        self.eraser_indicator = tk.Canvas(eraser_frame, width=14, height=14,
                                          highlightthickness=0)  # Создаем индикатор состояния ластика
        self.eraser_indicator.pack(side=tk.LEFT, padx=2)  # Размещаем индикатор слева с отступом
        self.eraser_indicator.create_oval(2, 2, 12, 12, fill='gray', outline='gray',
                                          tags="indicator")  # Рисуем серый кружок

        brush_size_frame = tk.LabelFrame(control_frame, text="Выбор размера кисти",
                                         height=50)  # Создаем рамку для элементов управления размером кисти
        brush_size_frame.pack(side=tk.LEFT, padx=5, pady=5,
                              fill=tk.Y)  # Размещаем рамку слева с отступами и заполнением по вертикали

        self.brush_size_var = tk.IntVar(value=5)  # Создаем переменную для хранения размера кисти (по умолчанию 5)

        self.brush_size_scale = tk.Scale(brush_size_frame, from_=1, to=10, orient=tk.HORIZONTAL,
                                         variable=self.brush_size_var, command=self.update_menu_from_scale)
        # Создаем шкалу для выбора размера кисти
        self.brush_size_scale.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем шкалу слева с отступами

        sizes = [1, 2, 5, 10]  # Список доступных размеров кисти
        self.selected_size = tk.StringVar(
            value=str(sizes[2]))  # Создаем переменную для хранения выбранного размера (по умолчанию "5")

        self.brush_size_menu = tk.OptionMenu(brush_size_frame, self.selected_size, *sizes,
                                             command=self.update_scale_from_menu)  # Создаем выпадающий список для
        # выбора размера кисти
        self.brush_size_menu.config(width=3)  # Устанавливаем ширину выпадающего списка
        self.brush_size_menu.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем список слева с отступами

        self.mode_label = tk.Label(eraser_frame, text="Режим: Кисть")  # Создаем метку для отображения текущего режима
        self.mode_label.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем метку слева с отступами

        self.brush_color_indicator = tk.Canvas(eraser_frame, width=14, height=14,
                                               highlightthickness=0)  # Создаем индикатор цвета кисти
        self.brush_color_indicator.pack(side=tk.LEFT, padx=2)  # Размещаем индикатор слева с отступом
        self.brush_color_indicator.create_oval(2, 2, 12, 12, fill='black', outline='black',
                                               tags="indicator_brush")  # Рисуем черный кружок

        self.root.bind('<Control-s>', self.save_image)  # Привязываем Ctrl+s к функции сохранения изображения
        self.root.bind('<Control-c>', self.choose_color)  # Привязываем Ctrl+c к функции выбора цвета

    def update_menu_from_scale(self, value):
        """Обновляет значение в выпадающем списке при изменении значения шкалы."""
        self.selected_size.set(value)  # Устанавливаем значение выбранного размера

    def update_scale_from_menu(self, value):
        """Обновляет значение шкалы при выборе значения из выпадающего списка."""
        self.brush_size_var.set(int(value))  # Устанавливаем значение размера кисти

    def paint(self, event):
        """Рисует линию на холсте и на изображении PIL при движении мыши."""
        if self.text_mode:  # Если включен режим добавления текста, не рисуем
            return

        if self.last_x and self.last_y:  # Если есть предыдущие координаты
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                    width=self.brush_size_var.get(),  # Используем текущий размер кисти
                                    fill=self.pen_color,
                                    capstyle=tk.ROUND, smooth=tk.TRUE)  # Рисуем линию на холсте
            self.draw.line([self.last_x, self.last_y, event.x, event.y], fill=self.pen_color,
                           width=self.brush_size_var.get())  # Рисуем линию на изображении PIL

        self.last_x = event.x  # Обновляем координаты предыдущей точки
        self.last_y = event.y

    def reset(self, event):
        """Сбрасывает координаты предыдущей точки."""
        self.last_x, self.last_y = None, None  # Сбрасываем координаты

    def clear_canvas(self):
        """Очищает холст и создает новое белое изображение."""
        self.canvas.delete("all")  # Очищаем холст
        self.image = Image.new("RGB", (850, 500), "white")  # Создаем новое изображение PIL
        self.draw = ImageDraw.Draw(self.image)  # Создаем объект для рисования на изображении

    def choose_color(self, event=None):
        """Открывает диалог выбора цвета и обновляет текущий цвет кисти."""
        chosen_color = colorchooser.askcolor(color=self.pen_color)[1]  # Открываем диалог выбора цвета
        if chosen_color:  # Если цвет выбран
            self.pen_color = chosen_color  # Обновляем цвет кисти
            self.previous_color = self.pen_color  # Обновляем предыдущий цвет
            self.eraser_mode = False  # Выключаем режим ластика
            self.update_mode_label()  # Обновляем метку режима
            self.update_eraser_indicator()  # Обновляем индикатор ластика
            self.update_brush_color_indicator()  # Обновляем индикатор цвета кисти
            self.update_mode_label_color()  # Обновляем цвет метки режима

    def save_image(self, event=None):
        """Открывает диалог сохранения файла и сохраняет изображение в формате PNG."""
        file_path = filedialog.asksaveasfilename(defaultextension='.png',  # Расширение по умолчанию
                                                 filetypes=[('PNG files', '*.png')],  # Типы файлов
                                                 title="Сохранить изображение как")  # Заголовок диалога
        if file_path:  # Если путь к файлу выбран
            self.image.save(file_path)  # Сохраняем изображение
            messagebox.showinfo("Информация", "Изображение успешно сохранено!")  # Показываем сообщение

    def toggle_eraser(self):
        """Переключает режим ластика."""
        self.eraser_mode = not self.eraser_mode  # Инвертируем режим ластика
        if self.eraser_mode:  # Если включен режим ластика
            self.previous_color = self.pen_color  # Сохраняем текущий цвет кисти
            self.pen_color = self.canvas['bg']  # Устанавливаем цвет ластика равным цвету фона
        else:  # Если выключен режим ластика
            self.pen_color = self.previous_color  # Восстанавливаем предыдущий цвет кисти
        self.update_mode_label()  # Обновляем метку режима
        self.update_eraser_indicator()  # Обновляем индикатор ластика
        self.update_brush_color_indicator()  # Обновляем индикатор цвета кисти
        self.update_mode_label_color()  # Обновляем цвет метки режима

    def update_mode_label(self):
        """Обновляет текст метки режима в зависимости от значения self.eraser_mode."""
        if self.eraser_mode:  # Если включен режим ластика
            self.mode_label.config(text="Режим: Ластик")  # Устанавливаем текст метки "Режим: Ластик"
        else:  # Если выключен режим ластика
            self.mode_label.config(text="Режим: Кисть")  # Устанавливаем текст метки "Режим: Кисть"

    def update_eraser_indicator(self):
        """Обновляет цвет индикатора ластика."""
        if self.eraser_mode:  # Если включен режим ластика
            self.eraser_indicator.itemconfig("indicator", fill=self.pen_color,
                                             outline="black")  # Устанавливаем цвет индикатора равным цвету ластика
        else:  # Если выключен режим ластика
            self.eraser_indicator.itemconfig("indicator", fill="gray",
                                             outline="gray")  # Устанавливаем серый цвет индикатора

    def pick_color(self, event):
        """
        Выбирает цвет пикселя на холсте под курсором мыши (правая кнопка).
        Устанавливает цвет кисти равным цвету выбранного пикселя.
        """
        x, y = event.x, event.y  # Получаем координаты клика
        try:
            rgb = self.image.getpixel((x, y))  # Получаем RGB цвет пикселя из изображения PIL
            hex_color = "#{:02x}{:02x}{:02x}".format(*rgb)  # Преобразуем RGB в HEX
        except IndexError:
            messagebox.showwarning("Внимание", "Вы кликнули за пределами холста!")  # Показываем предупреждение
            return  # Прерываем выполнение, чтобы избежать ошибки

        self.pen_color = hex_color  # Устанавливаем цвет кисти равным выбранному цвету
        self.previous_color = self.pen_color  # Обновляем предыдущий цвет кисти
        self.eraser_mode = False  # Выключаем режим ластика
        self.update_mode_label()  # Обновляем метку режима
        self.update_eraser_indicator()  # Обновляем индикатор ластика
        self.update_brush_color_indicator()  # Обновляем индикатор цвета кисти
        self.update_mode_label_color()  # Обновляем цвет метки режима

    def update_brush_color_indicator(self):
        """Обновляет цвет индикатора цвета кисти."""
        self.brush_color_indicator.itemconfig("indicator_brush", fill=self.pen_color,
                                              outline=self.pen_color)  # Устанавливаем цвет индикатора равным цвету
        # кисти

    def update_mode_label_color(self):
        """Обновляет цвет текста метки режима в соответствии с цветом кисти."""
        if self.eraser_mode:  # Если включен режим ластика
            self.mode_label_fg = "black"  # Устанавливаем черный цвет текста метки
        else:  # Если выключен режим ластика
            self.mode_label_fg = self.pen_color  # Устанавливаем цвет текста метки равным цвету кисти
        self.mode_label.config(foreground=self.mode_label_fg)  # Применяем цвет текста к метке

    def resize_canvas(self):
        """Открывает диалоговое окно для ввода новых размеров холста и обновляет холст."""
        new_width = simpledialog.askinteger("Изменение размера", "Введите новую ширину холста:", minvalue=100,
                                            maxvalue=2000)  # Запрашиваем новую ширину холста
        new_height = simpledialog.askinteger("Изменение размера", "Введите новую высоту холста:", minvalue=100,
                                             maxvalue=2000)  # Запрашиваем новую высоту холста
        if new_width is not None and new_height is not None:  # Если размеры введены
            self.canvas.config(width=new_width, height=new_height)  # Устанавливаем новые размеры холста
            self.image = Image.new("RGB", (new_width, new_height), "white")  # Создаем новое изображение PIL
            self.draw = ImageDraw.Draw(self.image)  # Создаем объект для рисования на изображении
            self.canvas.delete("all")  # Очищаем холст

    def change_background(self):
        """
        Открывает диалоговое окно для выбора цвета и изменяет фон холста.
        Если ластик был включен, сразу меняем цвет ластика на новый цвет фона.
        """
        chosen_color = colorchooser.askcolor(color=self.canvas['bg'])[1]  # Открываем диалог выбора цвета
        if chosen_color:  # Если цвет выбран
            self.canvas.config(bg=chosen_color)  # Устанавливаем новый цвет фона холста
            if self.eraser_mode:  # Если включен режим ластика
                self.pen_color = chosen_color  # Устанавливаем цвет ластика равным цвету фона
                self.update_eraser_indicator()  # Обновляем индикатор ластика
                self.update_brush_color_indicator()  # Обновляем индикатор цвета кисти

    def start_text_mode(self):
        """
        Активирует режим ввода текста: запрашивает у пользователя строку и размер шрифта в одном диалоге.
        Использование лямбда-функции для упрощения кода и избежания дублирования.
        """

        def place_text_wrapper(text, size):
            """Замыкание для передачи текста и размера в place_text."""
            self.entered_text = text  # Сохраняем введенный текст
            self.text_size = size  # Сохраняем выбранный размер шрифта
            self.text_mode = True  # Включаем режим текста
            messagebox.showinfo("Режим текста",
                                "Кликните левой кнопкой мыши по холсту, чтобы добавить текст.")  # Показываем сообщение
            self.canvas.bind("<Button-1>", self.place_text)  # Привязываем клик левой кнопкой мыши к функции place_text

        self.open_text_input_dialog(place_text_wrapper)  # Открываем диалог ввода текста и размера шрифта

    def open_text_input_dialog(self, callback):
        """
        Открывает диалоговое окно для ввода текста и размера шрифта.
        Аргумент callback - функция, которая будет вызвана с введённым текстом и размером шрифта.
        """
        dialog = tk.Toplevel(self.root)  # Создаем диалоговое окно
        dialog.title("Введите текст и размер шрифта")  # Устанавливаем заголовок диалога

        text_label = tk.Label(dialog, text="Текст:")  # Создаем метку для поля ввода текста
        text_label.grid(row=0, column=0, padx=5, pady=5)  # Размещаем метку в диалоге
        text_entry = tk.Entry(dialog)  # Создаем поле ввода текста
        text_entry.grid(row=0, column=1, padx=5, pady=5)  # Размещаем поле ввода в диалоге

        size_label = tk.Label(dialog, text="Размер шрифта:")  # Создаем метку для поля ввода размера шрифта
        size_label.grid(row=1, column=0, padx=5, pady=5)  # Размещаем метку в диалоге
        size_entry = tk.Entry(dialog)  # Создаем поле ввода размера шрифта
        size_entry.insert(0, str(self.text_size))  # Задаем значение по умолчанию
        size_entry.grid(row=1, column=1, padx=5, pady=5)  # Размещаем поле ввода в диалоге

        def apply_and_close():
            """Функция для применения введенного текста и размера шрифта и закрытия диалога."""
            text = text_entry.get()  # Получаем введенный текст
            try:
                size = int(size_entry.get())  # Получаем введенный размер шрифта
                if not text.strip():  # Проверяем, что текст не пустой
                    messagebox.showwarning("Внимание", "Текст не может быть пустым.")  # Показываем предупреждение
                    return  # Прерываем выполнение

                if size <= 0:  # Проверяем, что размер шрифта положительный
                    messagebox.showwarning("Внимание",
                                           "Размер шрифта должен быть положительным числом.")  # Показываем
                    # предупреждение
                    return  # Прерываем выполнение

                callback(text, size)  # Вызываем callback-функцию с текстом и размером шрифта
                dialog.destroy()  # Закрываем диалоговое окно
            except ValueError:
                messagebox.showerror("Ошибка",
                                     "Неверный формат размера шрифта. Введите целое число.")  # Показываем сообщение
                # об ошибке

        apply_button = tk.Button(dialog, text="Применить", command=apply_and_close)  # Создаем кнопку "Применить"
        apply_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)  # Размещаем кнопку в диалоге

    def place_text(self, event):
        """
        Размещает текст на холсте и на PIL-изображении в точке клика.
        Отключает режим текста после размещения.
        Использует выбранный (self.text_size) размер шрифта,
        пытается загрузить Arial, если не доступен - использует стандартный шрифт PIL.
        """
        if self.text_mode and self.entered_text:  # Проверяем, включен ли режим текста и введен ли текст
            x, y = event.x, event.y  # Получаем координаты клика

            # Пытаемся загрузить шрифт Arial
            try:
                font = ImageFont.truetype("arial.ttf", self.text_size)  # Пытаемся загрузить шрифт Arial
            except OSError:
                # Если arial.ttf не найден, используем стандартный шрифт PIL
                font = ImageFont.load_default()  # Загружаем шрифт по умолчанию
                messagebox.showwarning("Внимание",
                                       "Шрифт Arial не найден. Используется шрифт по умолчанию.")  # Показываем
                # предупреждение

            # Рисуем текст на холсте Tkinter
            self.canvas.create_text(x, y, text=self.entered_text, fill=self.pen_color,
                                    anchor='nw', font=("TkDefaultFont", self.text_size))  # Создаем текст на холсте

            # Рисуем текст на изображении PIL - **Исправлено**
            self.draw.text((x, y), self.entered_text, fill=self.pen_color, font=font)  # Рисуем текст на изображении

            self.text_mode = False  # Выключаем режим текста
            self.entered_text = None  # Очищаем введенный текст

            # Восстанавливаем привязку рисования
            self.canvas.unbind("<Button-1>")  # Убираем привязку place_text к кнопке 1
            self.canvas.bind("<B1-Motion>", self.paint)  # Восстанавливаем привязку рисования
            self.canvas.bind("<ButtonRelease-1>", self.reset)  # Восстанавливаем привязку сброса координат


def main():
    """
    Создает главное окно приложения и запускает основной цикл обработки событий.
    """
    root = tk.Tk()  # Создаем главное окно
    app = DrawingApp(root)  # Создаем экземпляр приложения
    root.mainloop()  # Запускаем главный цикл обработки событий


if __name__ == "__main__":
    main()  # Запускаем приложение
