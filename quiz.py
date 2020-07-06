import os, sys, time, threading, functools, json
import tkinter.ttk as ttk

from tkinter import Tk, Frame, LabelFrame, Button, Label, PhotoImage, Radiobutton, Menu, StringVar, IntVar
from PIL import Image, ImageTk

# Defining the variables for the quiz.
class Variables():
    def __init__(self):
        self.questions = {}
        self.name = StringVar()
        self.desc = StringVar()
        self.time_text = StringVar()
        self.correct_text = StringVar()
        self.in_progress = False

    def set_info(self):
        self.name.set(self.questions["name"])
        self.desc.set(self.questions["desc"])

# Initializing the GUI for the quiz, along with the implementation of dynamically-created widgets.
class QuizGUI(Frame):
    def __init__(self, master=None):
        self.widget_list = []
        self.image_list = []
        self.button_list = []
        self.current_tab = 0

        Frame.__init__(self, master)
        self.style_manager = ttk.Style()
        self.style_manager.theme_use("xpnative")
        self.style_manager.layout("TNotebook.Tab", [])
        self.master.title("Python Quiz Framework")
        self.master.resizable(False, False)
        # self.master.attributes('-topmost', True)
        self.master.grid_columnconfigure(1, weight=1, uniform="col")
        self.master.grid_columnconfigure(2, weight=1, uniform="col")
        self.grid(column=0, row=0, padx=(20,20), pady=(10,20))

        self.menubar = Menu(self)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Open")
        self.filemenu.add_command(label="Exit", command=self.destroy)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About")
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.master.config(menu=self.menubar)

        self.info_frame = LabelFrame(self, text="Current quizset:")
        self.info_frame.grid(column=1, row=1, sticky="ew", padx=(0,8))
        self.quiz_name_label = Label(self.info_frame, text="Name:")
        self.quiz_name_label.grid(column=0, row=0, padx=(10,0), pady=(10,0), sticky="w")
        self.quiz_name = Label(self.info_frame, textvariable=var.name)
        self.quiz_name.grid(column=1, row=0, padx=(0,10), pady=(10,0), sticky="w")
        self.quiz_desc_label = Label(self.info_frame, text="Description:")
        self.quiz_desc_label.grid(column=0, row=1, padx=(10,0), pady=(0,10), sticky="w")
        self.quiz_desc = Label(self.info_frame, textvariable=var.desc)
        self.quiz_desc.grid(column=1, row=1, padx=(0,10), pady=(0,10), sticky="w")
        self.quiz_load = Button(self.info_frame, text="Load quiz")

        self.stat_frame = LabelFrame(self, text="Statistics:")
        self.stat_frame.grid(column=2, row=1, sticky="ew", padx=(8,0))
        self.timer_label = Label(self.stat_frame, text="Time:")
        self.timer_label.grid(column=0, row=0, padx=(10,0), pady=(10,0), sticky="w")
        self.timer = Label(self.stat_frame, textvariable=var.time_text)
        self.timer.grid(column=1, row=0, padx=(0,10), pady=(10,0), sticky="w")
        self.score_label = Label(self.stat_frame, text="Correct:")
        self.score_label.grid(column=0, row=1, padx=(10,0), pady=(0,10), sticky="w")
        self.score = Label(self.stat_frame, textvariable=var.correct_text)
        self.score.grid(column=1, row=1, padx=(0,10), pady=(0,10), sticky="w")

        self.quiz_frame = LabelFrame(self, text="Quiz:")
        self.quiz_frame.grid(column=1, row=2, pady=(10,10), columnspan=2)
        self.quiz_notebook = ttk.Notebook(self.quiz_frame)
        self.quiz_notebook.grid(column=0, row=1, padx=(10,10), pady=(10,10))
        self.add_questions()

        self.options_frame = Frame(self)
        self.options_frame.grid(column=1, row=3, columnspan=2)
        self.start_button = Button(self.options_frame, text="Start", command=handler.start_quiz)
        self.start_button.grid(column=0, row=0, ipadx=20, ipady=5, padx=(0,10))
        self.reset_button = Button(self.options_frame, text="Reset", state="disabled", command=handler.reset_quiz)
        self.reset_button.grid(column=1, row=0, ipadx=20, ipady=5, padx=(0,0))

    def add_questions(self):
        for q in range(0, len(var.questions["questions"])):
            self.question_num = "Question " + str(q+1)
            self.current_question = var.questions["questions"][q]["question"]
            self.current_image = var.questions["questions"][q]["image"]
            self.answer_list = var.questions["questions"][q]["answers"]

            self.question_frame = Frame(self.quiz_notebook)
            self.quiz_notebook.add(self.question_frame, text=self.question_num)
            self.question_label = Label(self.question_frame, text=self.current_question)
            self.question_label.grid(column=0, row=0, padx=(10,10), pady=(10,10))
            self.image_obj = ImageTk.PhotoImage(Image.open(self.current_image))
            self.image_list.append(self.image_obj)
            self.question_image = Label(self.question_frame, image=self.image_list[q], relief="ridge")
            self.question_image.grid(column=0, row=1, padx=(10,10), pady=(0,10))
            for i in enumerate(self.answer_list):
                # Refrain from using lambda to attach a function without initially triggering it,
                # as the argument doesn't get passed until the very last iteration of the for loop.
                self.quiz_answer = Button(self.question_frame, text=i[1]["text"], command=functools.partial(self.add_check, answer_arg=i[1]["key"], question_idx=q))
                self.button_list.append(self.quiz_answer)
                self.quiz_answer.grid(column=0, row=2+i[0], padx=(10,10), ipady=10, sticky="ew")

    def add_check(self, answer_arg, question_idx):
        handler.check_answers(answer_arg, question_idx)

class FileHandler():
    def __init__(self):
        with open("python_quizset.json", "r") as quizset:
            quizset_data = quizset.read()
            quiz_dict = json.loads(quizset_data)
            var.questions = quiz_dict
        var.set_info()

# Handler for various tasks related to the quiz.
class QuizHandler():
    def __init__(self):
        self.measured_time = 0
        self.correct_int = 0
        self.set_time()
        self.set_answer()

    def set_answer(self):
        var.correct_text.set(str(self.correct_int) + "/" + str(len(var.questions["questions"])))

    def set_time(self):
        var.time_text.set(str(self.measured_time) + "s")

    def timer(self):
        while var.in_progress == True:
            self.measured_time += 1
            self.set_time()
            time.sleep(1)
        self.set_time()

    def start_quiz(self):
        var.in_progress = True
        for frame in gui.quiz_notebook.winfo_children():
            for wdg in frame.winfo_children():
                wdg.configure(state="active")
        self.time_thread = threading.Thread(target=self.timer, daemon=True)
        self.measured_time = 0
        self.correct_int = 0
        self.set_time()
        self.set_answer()
        self.time_thread.start()
        gui.start_button.configure(state="disabled")
        gui.reset_button.configure(state="active")

    def reset_quiz(self):
        var.in_progress = False
        for frame in gui.quiz_notebook.winfo_children():
            for wdg in frame.winfo_children():
                wdg.configure(state="disabled")
        self.measured_time = 0
        self.correct_int = 0
        self.set_time()
        # Approximate time it takes for the timer thread to stop, this is a workaround 
        # and should not be implemented in production. However, this is a personal project.
        time.sleep(1)
        gui.start_button.configure(state="active")
        gui.reset_button.configure(state="disabled")

    def check_answers(self, answer, index):
        if answer == var.questions["questions"][index]["correct"] and self.correct_int < len(var.questions["questions"]):
            self.correct_int += 1
            self.set_answer()
            if gui.current_tab < len(var.questions["questions"]) - 1:
                gui.current_tab += 1
                gui.quiz_notebook.select(gui.current_tab)
            else:
                self.reset_quiz()

root = Tk()
var = Variables()
file_handler = FileHandler()
handler = QuizHandler()

gui = QuizGUI(root)

handler.reset_quiz()

if __name__ == "__main__":
    root.mainloop()