#!/usr/bin/env python3
#   13CPT - Python Quiz Assessment
# -----------------------------------
#   This could have been much easier if we were allowed to complete this standard using Java.
#   But, knowing NZQA, Python is the only way to go I guess. ¯\_(ツ)_/¯
# -----------------------------------
#   https://github.com/totenk0pf/13CPT-python
# -----------------------------------

import os, sys, time, threading, functools, json
import tkinter.ttk as ttk

from tkinter import Tk, Frame, LabelFrame, Button, Label, PhotoImage, Radiobutton, Menu, StringVar, IntVar, Toplevel, filedialog, simpledialog
from PIL import Image, ImageTk

# Defining the variables for the quiz.
class Variables():
    def __init__(self):
        self.questions = {} # Question dictionary loaded from file.
        self.name = StringVar() # Name of the current quiz.
        self.desc = StringVar() # Description of the current quiz.
        self.time_text = StringVar() # Measured time.
        self.correct_text = StringVar() # Correct answers.
        self.in_progress = False # State of the quiz.
        self.current_tab = 0 # Current tab index.

    # Set the defined StringVars to the loaded variables.
    def set_info(self):
        self.name.set(self.questions["name"])
        self.desc.set(self.questions["desc"])

# Initializes the GUI for the quiz, along with the implementation of dynamically-created widgets.
class QuizGUI(Frame):
    def __init__(self, master=None):
        self.widget_list = [] # List to store dynamic widgets.
        self.image_list = [] # list to store image objects.
        self.button_list = [] # List to store answer buttons.

        Frame.__init__(self, master)
        self.style_manager = ttk.Style()
        self.style_manager.layout("TNotebook.Tab", [])
        self.master.title("Python Quiz Framework")
        self.master.resizable(False, False)
        self.grid(column=0, row=0, padx=(20,20), pady=(10,20))

        self.menubar = Menu(self)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load quiz", command=lambda: file_handler.parse_file(filedialog.askopenfile("r")))
        self.filemenu.add_command(label="Leaderboard", command=handler.show_leaderboard)
        self.filemenu.add_command(label="Exit", command=root.destroy)
        self.menubar.add_cascade(label="Quiz", menu=self.filemenu)
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About")
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.master.config(menu=self.menubar)

        self.info_frame = LabelFrame(self, text="Current quiz:")
        self.info_frame.grid(column=0, row=0, padx=(0,10), sticky="nsew")
        self.quiz_name_label = Label(self.info_frame, text="Name:")
        self.quiz_name_label.grid(column=0, row=0, padx=(10,0), pady=(10,0), sticky="w")
        self.quiz_name = Label(self.info_frame, textvariable=var.name)
        self.quiz_name.grid(column=1, row=0, padx=(0,10), pady=(10,0), sticky="w")
        self.quiz_desc_label = Label(self.info_frame, text="Description:")
        self.quiz_desc_label.grid(column=0, row=1, padx=(10,0), pady=(0,10), sticky="nw")
        self.quiz_desc = Label(self.info_frame, textvariable=var.desc, justify="left")
        self.quiz_desc.grid(column=1, row=1, padx=(0,10), pady=(0,10), sticky="w")

        self.stat_frame = LabelFrame(self, text="Statistics:")
        self.stat_frame.grid(column=1, row=0, sticky="nsew", padx=(10,0))
        self.timer_label = Label(self.stat_frame, text="Time:")
        self.timer_label.grid(column=0, row=0, padx=(10,0), pady=(10,0), sticky="w")
        self.timer = Label(self.stat_frame, textvariable=var.time_text)
        self.timer.grid(column=1, row=0, padx=(0,10), pady=(10,0), sticky="w")
        self.score_label = Label(self.stat_frame, text="Correct:")
        self.score_label.grid(column=0, row=1, padx=(10,0), pady=(0,10), sticky="w")
        self.score = Label(self.stat_frame, textvariable=var.correct_text)
        self.score.grid(column=1, row=1, padx=(0,10), pady=(0,10), sticky="w")

        self.quiz_frame = LabelFrame(self, text="Quiz:")
        self.quiz_frame.grid(column=0, row=1, pady=(10,10), columnspan=2, sticky="ew")
        self.quiz_notebook = ttk.Notebook(self.quiz_frame)
        self.quiz_notebook.grid(column=0, row=1, padx=(10,10), pady=(10,10), sticky="ew")
        self.add_questions()

        self.options_frame = Frame(self)
        self.options_frame.grid(column=0, row=2, columnspan=2)
        self.start_button = Button(self.options_frame, text="Start", command=handler.start_quiz)
        self.start_button.grid(column=0, row=0, ipadx=20, ipady=5, padx=(0,10))
        self.reset_button = Button(self.options_frame, text="Reset", state="disabled", command=handler.reset_quiz)
        self.reset_button.grid(column=1, row=0, ipadx=20, ipady=5, padx=(0,10))
        self.board_button = Button(self.options_frame, text="Leaderboard", command=handler.show_leaderboard)
        self.board_button.grid(column=2, row=0, ipadx=20, ipady=5, padx=(0,10))
        self.load_button = Button(self.options_frame, text="Load quiz", command=lambda: file_handler.parse_file(filedialog.askopenfile("r")))
        self.load_button.grid(column=3, row=0, ipadx=20, ipady=5, padx=(0,0))

    # Dynamically create widgets based on pre-defined data
    def add_questions(self):
        for q in range(0, len(var.questions["questions"])): # Iterate through the pre-defined list of questions
            self.question_num = "Question " + str(q+1) + ": " # Question number
            self.current_question = self.question_num + var.questions["questions"][q]["question"] 
            self.current_image = var.questions["questions"][q]["image"]
            self.answer_list = var.questions["questions"][q]["answers"]

            self.question_frame = Frame(self.quiz_notebook)
            self.quiz_notebook.add(self.question_frame, text=self.question_num)
            self.question_label = Label(self.question_frame, text=self.current_question, wraplength=400)
            self.question_label.grid(column=0, row=0, padx=(0,10), pady=(10,10))
            self.image_obj = ImageTk.PhotoImage(Image.open(self.current_image))
            self.image_list.append(self.image_obj)
            self.question_image = Label(self.question_frame, image=self.image_list[q], relief="ridge")
            self.question_image.grid(column=0, row=1, padx=(10,10), pady=(0,10), sticky="ew")
            for i in enumerate(self.answer_list, 1):
                # Refrain from using lambda to attach a function without initially triggering it,
                # as the argument doesn't get passed until the very last iteration of the for loop.
                self.quiz_answer = Button(self.question_frame, text=i[1]["text"], command=functools.partial(self.add_check, answer_arg=i[1]["key"], question_idx=q))
                self.button_list.append(self.quiz_answer)
                # Check if the current answer is the last in the list.
                if i[0] % 4 != 0:
                    self.quiz_answer.grid(column=0, row=2+i[0], padx=(10,10), ipady=10, sticky="ew")
                else:
                    self.quiz_answer.grid(column=0, row=2+i[0], padx=(10,10), pady=(0,10), ipady=10, sticky="ew")

    def add_check(self, answer_arg, question_idx):
        handler.check_answers(answer_arg, question_idx)

# Initializes and hides the results window.
class ResultGUI(Toplevel):
    def __init__(self, master=None):
        Toplevel.__init__(self, master)
        self.title("Result")
        self.resizable(False, False)
        self.final_time = StringVar() # Final displayed time.
        self.final_score = StringVar() # Final displayed score.
        self.final_msg = StringVar() # Message displayed based on scores.
        # List with the format (lower boundary, upper boundary, message) to display a message based on the correct percentage.
        self.msg_list = [
            (0, 20, "Are you even trying?"),
            (20, 40, "Try harder!"),
            (40, 60, "Keep trying!"),
            (60, 80, "You're getting there!"),
            (80, 100, "Almost there!"),
            (100, 100, "Perfect score!")
        ]
        self.columnconfigure(0, weight=1, uniform="col")
        self.columnconfigure(1, weight=1, uniform="col")

        self.stat_frame = LabelFrame(self, text="Final results:")
        self.stat_frame.grid(column=0, row=0, padx=(20,20), pady=(20,0), sticky="ew", columnspan=2)
        self.stat_frame.columnconfigure(0, weight=0)
        self.stat_frame.columnconfigure(1, weight=0)
        self.timer_label = Label(self.stat_frame, text="Time:")
        self.timer_label.grid(column=0, row=0, padx=(10,0), pady=(10,0), sticky="ew")
        self.timer = Label(self.stat_frame, textvariable=self.final_time, justify="center")
        self.timer.grid(column=1, row=0, padx=(0,10), pady=(10,0), sticky="ew")
        self.score_label = Label(self.stat_frame, text="Correct:")
        self.score_label.grid(column=0, row=1, padx=(10,0), pady=(0,10), sticky="ew")
        self.score = Label(self.stat_frame, textvariable=self.final_score, justify="center")
        self.score.grid(column=1, row=1, padx=(0,10), pady=(0,10), sticky="ew")
        self.msg = Label(self.stat_frame, textvariable=self.final_msg)
        self.msg.grid(column=0, row=2, padx=(10,10), pady=(0,10), columnspan=2)
        self.ok_button = Button(self, text="OK", command=self.hide)
        self.ok_button.grid(column=0, row=1, padx=(20,10), pady=(10,20), ipadx=10, ipady=5, sticky="ew")
        self.board_button = Button(self, text="Leaderboard", command=handler.show_leaderboard)
        self.board_button.grid(column=1, row=1, padx=(0,20), pady=(10,20), ipadx=10, ipady=5, sticky="ew")
        self.hide()

    # Set the results label, calculate percentage and set the message label.
    def get_results(self):
        self.final_time.set(var.time_text.get())
        self.final_score.set(var.correct_text.get())
        self.percentage = (handler.correct_int / len(var.questions["questions"])) * 100
        for i in self.msg_list:
            if i[0] <= self.percentage < i[1]:
                self.final_msg.set(i[2])

    def show(self):
        self.get_results()
        self.deiconify()
        self.lift()

    def hide(self):
        self.withdraw()

# Initializes and hides the leaderboard window.
class LeaderboardGUI(Toplevel):
    def __init__(self, master=None):
        Toplevel.__init__(self, master)
        self.title("Leaderboard")
        self.resizable(False, False)
        self.hide()

        self.board = ttk.Treeview(self)
        # Defining columns for the leaderboard.
        self.board["columns"] = ("1","2","3")
        self.board.column("#0", width="25", minwidth="25", stretch=False, anchor="w")
        self.board.column("1", width="100", minwidth="100", stretch=False)
        self.board.column("2", width="60", minwidth="60", stretch=False)
        self.board.column("3", width="60", minwidth="60", stretch=False)
        self.board.heading("#0", text="No.", anchor="w")
        self.board.heading("1", text="Name")
        self.board.heading("2", text="Score")
        self.board.heading("3", text="Time")
        self.board.grid(column=0, row=0, padx=(10,10), pady=(10,10))
        self.ok_button = Button(self, text="OK", command=self.hide)
        self.ok_button.grid(column=0, row=1, padx=(10,10), pady=(0,10), sticky="ew")
        
        self.board.bind("<Button-1>", self.handle_click)

    # Disables resizing of the columns by binding the mouseclick event.
    def handle_click(self, event):
        if self.board.identify_region(event.x, event.y) == "separator":
            return "break"

    def show(self):
        self.deiconify()
        file_handler.parse_leaderboard()

    def hide(self):
        self.withdraw()

# Handler for tasks related to loading files and parsing data from the aforementioned files.
class FileHandler():
    def __init__(self):
        # Default file is "python_quiz.json".
        self.current_file = "python_quiz" # Current filename without the extension.
        self.board_json = {} # Content of the leaderboard.
        # Parse the default quiz file.
        with open((self.current_file + ".json"), "r") as quiz:
            var.questions = json.loads(quiz.read())
        # Parse the leaderboard file.
        with open("leaderboard.json", "r") as board_file:
            self.board_json = json.loads(board_file.read())
        self.leader_list = self.board_json[self.current_file] # Assigning the key containing the current file's leaderboard to a list.
        self.leader_list.sort(key=lambda x: (x["score"]), reverse=True) # Sort the list by the players' time and score.
        var.set_info()

    # Open a file, destroy the existing widgets and create new ones based on the parsed data.
    def parse_file(self, file_obj):
        try:
            self.current_file = os.path.basename(file_obj.name).split(".")[0] # Set the filename variable to the parsed file object's name without the extension
            var.questions = json.loads(file_obj.read())
            var.set_info()
            for i in gui.quiz_notebook.winfo_children(): # Destroying widgets
                i.destroy()
            gui.add_questions()
            handler.reset_quiz()
        except:
            print("Tried to load invalid quiz.")

    # Open the leaderboard file, destroy the existing entries in the leaderboard widget and create new ones based on the parsed data.
    def parse_leaderboard(self):
        for i in leader_gui.board.get_children():
            leader_gui.board.delete(i)
        for i in enumerate(self.board_json[self.current_file], 1):
            leader_gui.board.insert("", "end", text=i[0], values=(i[1]["name"], i[1]["score"], i[1]["time"]))

    # Write the (modified) leaderboard dictionary to the .json file.
    def write_leaderboard(self):
        with open("leaderboard.json", "w") as board_file:
            json.dump(self.board_json, board_file, indent="\t")

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

    def set_state(self, state:str):
        for frame in gui.quiz_notebook.winfo_children():
            for wdg in frame.winfo_children():
                wdg.configure(state=state)

    # Starts the quiz
    def start_quiz(self):
        var.in_progress = True
        self.set_state("active")
        # Timer is being ran in another thread because using root.after() will literally freeze the main thread. 
        # The timer thread will be terminated upon exit as it is a daemon thread.
        self.time_thread = threading.Thread(target=self.timer, daemon=True)
        self.measured_time = 0
        self.correct_int = 0
        var.current_tab = 0
        gui.quiz_notebook.select(var.current_tab)
        self.set_time()
        self.set_answer()
        self.time_thread.start()
        gui.start_button.configure(state="disabled")
        gui.reset_button.configure(state="active")

    # Resets the quiz
    def reset_quiz(self):
        var.in_progress = False
        self.set_state("disabled")
        self.measured_time = 0
        self.correct_int = 0
        self.set_time()
        self.set_answer()
        # Approximate time it takes for the timer thread to stop, this is a workaround 
        # and should not be implemented in production. However, this is a personal project,
        # which means all of that shouldn't be an issue.
        time.sleep(1)
        gui.start_button.configure(state="active")
        gui.reset_button.configure(state="disabled")

    def finish_quiz(self):
        # # [DEPRECATED] Checks if the player has a new record by comparing their score and time to the first item in the leaderboard list.
        # if self.correct_int > int(file_handler.leader_list[0]["score"]):
            # if self.measured_time < int(file_handler.leader_list[0]["time"]):
        var.in_progress = False
        time.sleep(1)
        self.leader_name = simpledialog.askstring("Leaderboard", "Please enter your name below:")
        if self.leader_name is not None:
            file_handler.board_json[file_handler.current_file].append({"name": self.leader_name, "score": self.correct_int, "time": self.measured_time})
            file_handler.write_leaderboard()
            self.reset_quiz()
        else:
            self.reset_quiz()

    def check_finish(self):
        if var.current_tab < len(var.questions["questions"]) - 1:
            var.current_tab += 1
            gui.quiz_notebook.select(var.current_tab)
        else:
            result_gui.show()
            self.finish_quiz()

    # Checks the passed arguments by comparing them to the correct answer key provided in the Variables() class,
    # and proceeds to the next question if it is correct.
    def check_answers(self, answer:str, index:int):
        if answer == var.questions["questions"][index]["correct"] and self.correct_int < len(var.questions["questions"]):
            self.correct_int += 1
            self.set_answer()
            self.check_finish()
        else:
            self.set_answer()
            self.check_finish()

    def show_leaderboard(self):
        leader_gui.show()

# Initializing the classes
root = Tk()
var = Variables()
file_handler = FileHandler()
handler = QuizHandler()

gui = QuizGUI(root)
result_gui = ResultGUI(root)
leader_gui = LeaderboardGUI(root)

# Triggering a reset of the variables so the quiz starts disabled.
handler.reset_quiz()

if __name__ == "__main__":
    root.mainloop()