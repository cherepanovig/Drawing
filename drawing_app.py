import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw


class DrawingApp:
    """
    Приложение для рисования с возможностью сохранения в формате PNG.

    Позволяет пользователю рисовать на холсте, выбирать цвет и размер кисти,
    очищать холст и сохранять рисунок в файл.

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
    """

    def __init__(self, root):
        """
        Инициализирует приложение DrawingApp.

        """
        self.root = root
        self.root.title("Рисовалка с сохранением в PNG")

        self.image = Image.new("RGB", (600, 400), "white")  # Создаем новое изображение PIL белого цвета
        self.draw = ImageDraw.Draw(self.image)  # Создаем объект ImageDraw для рисования на изображении

        self.canvas = tk.Canvas(root, width=600, height=400, bg='white')  # Создаем холст Tkinter
        self.canvas.pack()  # Размещаем холст в окне

        self.setup_ui()  # Настраиваем пользовательский интерфейс

        self.last_x, self.last_y = None, None  # Инициализируем координаты предыдущей точки (None, None в начале рисования)
        self.pen_color = 'black'  # Инициализируем цвет пера (по умолчанию черный)

        self.canvas.bind('<B1-Motion>', self.paint)  # Привязываем событие движения мыши с зажатой левой кнопкой к
        # методу paint
        self.canvas.bind('<ButtonRelease-1>', self.reset)  # Привязываем событие отпускания левой кнопки мыши к
        # методу reset

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

        # Рамка для выбора размера кисти
        brush_size_frame = tk.LabelFrame(control_frame,
                                         text="Выбор размера кисти")  # Создаем LabelFrame (рамка с заголовком)
        brush_size_frame.pack(side=tk.LEFT, padx=5, pady=5)  # Размещаем рамку слева с отступами

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
        self.image = Image.new("RGB", (600, 400), "white")  # Создаем новое изображение PIL
        self.draw = ImageDraw.Draw(self.image)  # Создаем новый объект ImageDraw для нового изображения

    def choose_color(self):
        """
        Открывает диалог выбора цвета и обновляет текущий цвет кисти.
        """
        chosen_color = colorchooser.askcolor(color=self.pen_color)[1]  # Открываем диалог выбора цвета
        if chosen_color:  # Проверяем, был ли выбран цвет
            self.pen_color = chosen_color  # Обновляем цвет кисти

    def save_image(self):
        """
        Открывает диалог сохранения файла и сохраняет изображение в формате PNG.
        """
        file_path = filedialog.asksaveasfilename(defaultextension='.png',  # Задаем расширение по умолчанию
                                                 filetypes=[('PNG files', '*.png')],  # Указываем типы файлов
                                                 title="Сохранить изображение как")
        if file_path:  # Проверяем, был ли выбран путь к файлу
            self.image.save(file_path)  # Сохраняем изображение
            messagebox.showinfo("Информация", "Изображение успешно сохранено!")  # Показываем сообщение


def main():
    """
    Создает главное окно приложения и запускает основной цикл обработки событий.
    """
    root = tk.Tk()  # Создаем главное окно
    app = DrawingApp(root)  # Создаем экземпляр приложения
    root.mainloop()  # Запускаем главный цикл обработки событий Tkinter


if __name__ == "__main__":
    main()
