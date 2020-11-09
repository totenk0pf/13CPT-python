#!/usr/bin/env python3
#   13CPT - Python Quiz Assessment
# -----------------------------------
#   https://github.com/totenk0pf/13CPT-python
# -----------------------------------

import os, sys, time, threading, functools, json, random
import tkinter.ttk as ttk
import webbrowser

from tkinter import Tk, Frame, LabelFrame, Button, Label, PhotoImage, Radiobutton, Menu, StringVar, IntVar, Toplevel, Listbox, filedialog, simpledialog

# Defining the variables for the quiz.
class Variables():
    """Class for variable storage and handling.
    """
    def __init__(self):
        self.questions = {} # Question dictionary loaded from file.
        self.name = StringVar() # Name of the current quiz.
        self.desc = StringVar() # Description of the current quiz.
        self.time_text = StringVar() # Measured time.
        self.correct_text = StringVar() # Correct answers.
        self.in_progress = False # State of the quiz.
        self.current_tab = 0 # Current tab index.
        self.FONT = ("Verdana", 8) # Current font.
        self.HELP_URL = lambda: webbrowser.open_new_tab("https://github.com/totenk0pf/13CPT-python/")

    def set_info(self):
        """Set the defined StringVars to the loaded variables.
        """
        self.name.set(self.questions["name"])
        self.desc.set(self.questions["desc"])

class LoadGUI(Frame):
    """Loading frame which allows the users to pick quizzes.
    """
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid(row=0, column=0, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.cover_photo = PhotoImage(file="static/cover.png")
        self.cover_label = Label(self, image=self.cover_photo)
        self.cover_label.grid(row=0, column=0, padx=(20,20), pady=(20,10), sticky="ew")
        self.select_frame = LabelFrame(self, text="Select a quiz")
        self.select_frame.grid(row=1, column=0, padx=(20,20), pady=(10,20), sticky="ew")
        for i in range(0,4):
            self.select_frame.grid_rowconfigure(i, weight=1)
        self.select_frame.grid_columnconfigure(0, weight=4)
        self.select_frame.grid_columnconfigure(1, weight=1)
        self.quiz_list = Listbox(self.select_frame)
        self.quiz_list.grid(row=0, column=0, rowspan=4, padx=(10,10), pady=(10,10), sticky="ew")
        self.start_button = Button(self.select_frame, text="Start quiz", command=self.start_chosen)
        self.start_button.grid(row=0, column=1, padx=(0,10), pady=(10,5), sticky="nsew")
        self.refresh_button = Button(self.select_frame, text="Refresh list", command=self.refresh)
        self.refresh_button.grid(row=1, column=1, padx=(0,10), pady=(5,5), sticky="nsew")
        self.help_button = Button(self.select_frame, text="Help", command=var.HELP_URL)
        self.help_button.grid(row=2, column=1, padx=(0,10), pady=(5,5), sticky="nsew")
        self.quit_button = Button(self.select_frame, text="Quit", command=root.destroy)
        self.quit_button.grid(row=3, column=1, padx=(0,10), pady=(5,10), sticky="nsew")
        self.get_quizzes()

    def get_quizzes(self):
        """[summary]
        """
        self.dir_list = sorted([i[:-5] for i in os.listdir() if i.endswith(".json") and "quiz" in i.lower()])
        for f in self.dir_list:
            self.quiz_list.insert("end", f)

    def refresh(self):
        """[summary]
        """
        self.quiz_list.delete(0, "end")
        self.get_quizzes()

    def start_chosen(self):
        """[summary]
        """
        self.filename = self.quiz_list.get("active") + ".json"
        file_handler.parse_file(self.filename)
        file_handler.parse_leaderboard()
        quiz_gui.add_questions()
        quiz_gui.tkraise()

class QuizGUI(Frame):
    """Initializes the GUI for the quiz, along with the implementation of dynamically-created widgets.
    """
    def __init__(self, master=None):
        self.widget_list = [] # List to store dynamic widgets.
        self.image_list = [] # list to store image objects.
        self.button_list = [] # List to store answer buttons.

        Frame.__init__(self, master)
        self.style_manager = ttk.Style()
        self.style_manager.layout("TNotebook.Tab", [])
        self.master.title("Quiz Framework")
        self.master.resizable(False, False)
        self.grid(column=0, row=0, padx=(20,20), pady=(10,20))

        self.menubar = Menu(self)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load quiz", command=self.raise_load)
        self.filemenu.add_command(label="Leaderboard", command=leader_gui.show)
        self.filemenu.add_command(label="Exit", command=root.destroy)
        self.menubar.add_cascade(label="Quiz", menu=self.filemenu)
        self.helpmenu = Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About", command=var.HELP_URL)
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
        self.quiz_frame.grid_columnconfigure(0, weight=1)
        self.quiz_frame.grid_rowconfigure(0, weight=1)
        self.quiz_notebook = ttk.Notebook(self.quiz_frame)
        self.quiz_notebook.grid(column=0, row=1, padx=(10,10), pady=(10,10), sticky="ew")
        self.add_questions()

        self.options_frame = Frame(self)
        self.options_frame.grid(column=0, row=2, columnspan=2, sticky="ew")
        for i in range(0,3):
            self.options_frame.grid_columnconfigure(i, weight=1)
        self.start_button = Button(self.options_frame, text="Start", command=handler.start_quiz)
        self.start_button.grid(column=0, row=0, ipadx=20, ipady=5, padx=(0,10), sticky="ew")
        self.reset_button = Button(self.options_frame, text="Reset", state="disabled", command=handler.reset_quiz)
        self.reset_button.grid(column=1, row=0, ipadx=20, ipady=5, padx=(0,10), sticky="ew")
        self.skip_button = Button(self.options_frame, text="Skip", command=self.skip)
        self.skip_button.grid(column=2, row=0, ipadx=20, ipady=5, padx=(0,10), sticky="ew")
        self.load_button = Button(self.options_frame, text="Load quiz", command=self.raise_load)
        self.load_button.grid(column=3, row=0, ipadx=20, ipady=5, padx=(0,0), sticky="ew")

    def add_questions(self):
        """Dynamically create widgets based on pre-defined data.
        """
        random.shuffle(var.questions["questions"]) # Shuffling questions
        self.image_list = []
        for q in range(0, len(var.questions["questions"])): # Iterate through the pre-defined list of questions
            random.shuffle(var.questions["questions"][q]["answers"])
            self.question_num = "Question " + str(q+1) + ": " # Question number
            self.current_question = self.question_num + var.questions["questions"][q]["question"] 
            self.current_image = var.questions["questions"][q]["image"]
            self.answer_list = var.questions["questions"][q]["answers"]

            self.question_frame = Frame(self.quiz_notebook)
            self.question_frame.grid_columnconfigure(0, weight=1)
            self.quiz_notebook.add(self.question_frame, text=self.question_num, sticky="nsew")
            self.question_label = Label(self.question_frame, text=self.current_question, wraplength=350)
            self.question_label.grid(column=0, row=0, padx=(10,10), pady=(10,10), sticky="ew")
            if self.current_image != "":
                self.image_obj = PhotoImage(file=self.current_image)
            else:
                self.image_obj = PhotoImage(file="static/blank.png")
            self.image_list.append(self.image_obj)
            self.question_image = Label(self.question_frame, image=self.image_list[q], relief="ridge")
            self.question_image.image = self.image_obj
            self.question_image.grid(column=0, row=1, padx=(10,10), pady=(0,10), sticky="ew")
            for i in enumerate(self.answer_list, 1):
                # Refrain from using lambda to attach a function without initially triggering it,
                # as the argument doesn't get passed until the very last iteration of the for loop.
                self.quiz_answer = Button(self.question_frame, text=i[1]["text"], command=functools.partial(self.ans_check, answer_arg=i[1]["key"], question_idx=q))
                self.button_list.append(self.quiz_answer)
                # Check if the current answer is the last in the list.
                if i[0] % 4 != 0:
                    self.quiz_answer.grid(column=0, row=2+i[0], padx=(10,10), ipady=10, sticky="ew")
                else:
                    self.quiz_answer.grid(column=0, row=2+i[0], padx=(10,10), pady=(0,10), ipady=10, sticky="ew")

    def kill_questions(self):
        """Kill all notebook frames.
        """
        for frame in quiz_gui.quiz_notebook.winfo_children():
            for wdg in frame.winfo_children():
                wdg.destroy()

    def raise_load(self):
        """Raise the loading frame.
        """
        self.load_confirm = simpledialog.messagebox.askyesno("Warning", "Your current progress will not be saved. Do you wish to continue?")
        if self.load_confirm:
            handler.reset_quiz()
            self.kill_questions()
            load_gui.tkraise()

    def ans_check(self, answer_arg:str, question_idx:int):
        """Check the answer by comparing it to the dictionary's answer key.
        """
        handler.check_answers(answer_arg, question_idx)

    def skip(self):
        """Skips the current question
        """
        pass
    
class ResultGUI(Toplevel):
    """Initializes and hides the result window.
    """
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
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")

        self.stat_frame = LabelFrame(self, text="Final results:")
        self.stat_frame.grid(column=0, row=0, padx=(20,20), pady=(20,0), sticky="ew", columnspan=2)
        self.stat_frame.grid_columnconfigure(0, weight=1)
        self.info_frame = Frame(self.stat_frame)
        self.info_frame.grid(column=0, row=0, sticky="ew")
        self.info_frame.grid_columnconfigure(0, weight=1)
        self.info_frame.grid_columnconfigure(1, weight=1)
        self.timer_label = Label(self.info_frame, text="Time:")
        self.timer_label.grid(column=0, row=0, padx=(0,0), pady=(10,0), sticky="ew")
        self.timer = Label(self.info_frame, textvariable=self.final_time, justify="center")
        self.timer.grid(column=1, row=0, padx=(0,0), pady=(10,0), sticky="ew")
        self.score_label = Label(self.info_frame, text="Correct:")
        self.score_label.grid(column=0, row=1, padx=(0,0), pady=(0,10), sticky="ew")
        self.score = Label(self.info_frame, textvariable=self.final_score, justify="center")
        self.score.grid(column=1, row=1, padx=(0,0), pady=(0,10), sticky="ew")
        self.msg = Label(self.info_frame, textvariable=self.final_msg)
        self.msg.grid(column=0, row=2, padx=(0,0), pady=(0,10), columnspan=2)
        self.ok_button = Button(self, text="OK", command=self.hide)
        self.ok_button.grid(column=0, row=1, padx=(20,10), pady=(10,20), ipadx=10, ipady=5, sticky="ew")
        self.board_button = Button(self, text="Leaderboard", command=leader_gui.show)
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

class LeaderboardGUI(Toplevel):
    """Initializes and hides the leaderboard window.
    """
    def __init__(self, master=None):
        Toplevel.__init__(self, master)
        self.title("Leaderboard")
        self.resizable(False, False)
        self.hide()

        self.board = ttk.Treeview(self)
        self.board["show"] = "headings"
        # Defining columns for the leaderboard.
        self.board["columns"] = ("Name", "Score", "Time")
        self.board.column("#0", width="25", minwidth="25", stretch=False, anchor="w")
        self.board.column("Name", width="100", minwidth="100", stretch=False)
        self.board.column("Score", width="60", minwidth="60", stretch=False)
        self.board.column("Time", width="60", minwidth="60", stretch=False)
        self.board.heading("Name", text="Name")
        self.board.heading("Score", text="Score")
        self.board.heading("Time", text="Time")
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

class FileHandler():
    """Handler for tasks related to loading files and parsing data from the aforementioned files.
    """
    def __init__(self):
        # Default file is "python_quiz.json".
        self.current_file = "Python Quiz" # Current filename without the extension.
        self.board_json = {} # Content of the leaderboard.
        # Parse the default quiz file.
        with open((self.current_file + ".json"), "r") as quiz:
            var.questions = json.loads(quiz.read())
        # Parse the leaderboard file.
        with open("leaderboard.json", "r") as board_file:
            self.board_json = json.loads(board_file.read())
        # Assigning the key containing the current file's leaderboard to a list.
        self.leader_list = self.board_json[self.current_file]
        # Sort the list by the players' time and score.
        self.leader_list.sort(key=lambda x: [x["score"], -x["time"]], reverse=True)
        # Sets the initial information.
        var.set_info()

    def parse_file(self, file_name:str):
        """Open a file, destroy the existing widgets and create new ones based on the parsed data.

        Args:
            file_name (str): Name of file to be parsed.
        """
        if os.path.isfile(file_name):
            with open(file_name) as file_obj:
                try:
                    # Set the filename variable to the parsed file object's name without the extension
                    self.current_file = os.path.basename(file_name).split(".")[0]
                    var.questions = json.loads(file_obj.read())
                    var.set_info()
                    # Destroying widgets
                    for i in quiz_gui.quiz_notebook.winfo_children():
                        i.destroy()
                    quiz_gui.add_questions()
                    handler.reset_quiz()
                except:
                    print("Tried to load invalid quiz.")
        else:
            print("File not found!")

    def parse_leaderboard(self):
        """Open the leaderboard file, destroy the existing entries in the leaderboard widget and create new ones based on the parsed data.
        """
        for i in leader_gui.board.get_children():
            leader_gui.board.delete(i)
        for i in enumerate(self.board_json[self.current_file], 1):
            leader_gui.board.insert("", "end", text=i[0], values=(i[1]["name"], i[1]["score"], i[1]["time"]))

    def write_leaderboard(self):
        """Write the (modified) leaderboard dictionary to the .json file.
        """
        with open("leaderboard.json", "w") as board_file:
            json.dump(self.board_json, board_file, indent="\t")

class QuizHandler():
    """Handler for various tasks related to the quiz.
    """
    def __init__(self):
        self.measured_time = 0
        self.correct_int = 0
        self.set_time()
        self.set_answer()

    def set_answer(self):
        """Updates the StringVar for the answer.
        """
        var.correct_text.set(str(self.correct_int) + "/" + str(len(var.questions["questions"])))

    def set_time(self):
        """Updates the StringVar for the time.
        """
        var.time_text.set(str(self.measured_time) + "s")

    def timer(self):
        """Adds the time up and updates the display while in_progress is set to True.
        """
        while var.in_progress == True:
            self.measured_time += 1
            self.set_time()
            time.sleep(1)
        self.set_time()

    def set_state(self, state:str):
        """Sets the main widgets' state to the passed argument.

        Args:
            state ("disabled", "active"): New state of the widgets.
        """
        for frame in quiz_gui.quiz_notebook.winfo_children():
            for wdg in frame.winfo_children():
                wdg.configure(state=state)

    def start_quiz(self):
        """Starts the quiz.
        """
        var.in_progress = True
        self.set_state("active")
        # Timer is being ran in another thread because using root.after() 
        # will literally freeze the main thread because of my spaghetti code.
        # The timer thread will be terminated upon exit as it is a daemon thread.
        self.time_thread = threading.Thread(target=self.timer, daemon=True)
        self.measured_time = 0
        self.correct_int = 0
        var.current_tab = 0
        quiz_gui.quiz_notebook.select(var.current_tab)
        self.set_time()
        self.set_answer()
        self.time_thread.start()
        quiz_gui.start_button.configure(state="disabled")
        quiz_gui.reset_button.configure(state="active")

    def reset_quiz(self):
        """Resets the quiz.
        """
        var.in_progress = False
        for i in quiz_gui.quiz_notebook.winfo_children(): # Destroying widgets
            i.destroy()
        quiz_gui.add_questions()
        self.set_state("disabled")
        self.measured_time = 0
        self.correct_int = 0
        self.set_time()
        self.set_answer()
        # Approximate time it takes for the timer thread to stop, this is a workaround 
        # and should not be implemented in production. However, this is a personal project,
        # which means all of that shouldn't be an issue.
        time.sleep(1)
        quiz_gui.start_button.configure(state="active")
        quiz_gui.reset_button.configure(state="disabled")

    def config_quiz(self, prog:bool, state:str, time:int, correct_ans:int):
        var.in_progress = prog
        self.set_state(state)
        self.measured_time = time
        self.correct_int = correct_ans
        self.set_time()
        self.set_answer()
        if prog == False:
            time.sleep(1)
            quiz_gui.start_button.configure(state="active")
            quiz_gui.reset_button.configure(state="disabled")

    def finish_quiz(self):
        var.in_progress = False
        time.sleep(1)
        while True:
            self.leader_name = simpledialog.askstring("Leaderboard", "Please enter your name below:")
            if self.leader_name is not None and self.leader_name.isalpha():
                file_handler.board_json[file_handler.current_file].append({"name": self.leader_name, "score": self.correct_int, "time": self.measured_time})
                file_handler.write_leaderboard()
                self.reset_quiz()
                break
            elif self.leader_name is None:
                self.reset_quiz()
                break
            else:
                simpledialog.messagebox.showwarning("Warning", "You've input an invalid name!")

    def check_finish(self):
        """Check if the quiz has reached its end or not.
        """
        if var.current_tab < len(var.questions["questions"]) - 1:
            var.current_tab += 1
            quiz_gui.quiz_notebook.select(var.current_tab)
        else:
            result_gui.show()
            self.finish_quiz()

    def check_answers(self, answer:str, index:int):
        """Checks the passed arguments by comparing them to the correct answer key provided in the Variables() class,
        and proceeds to the next question if it is correct.

        Args:
            answer (str): The answer key.
            index (int): The index of the current question.
        """
        if answer == var.questions["questions"][index]["correct"] and self.correct_int < len(var.questions["questions"]):
            self.correct_int += 1
            self.set_answer()
            self.check_finish()
        else:
            self.set_answer()
            self.check_finish()

root = Tk()
# Initializing the handler classes.
var = Variables()
file_handler = FileHandler()
handler = QuizHandler()
# Initializing the GUI classes.
leader_gui = LeaderboardGUI(root)
result_gui = ResultGUI(root)
load_gui = LoadGUI(root)
quiz_gui = QuizGUI(root)
load_gui.tkraise()
# Triggering a reset of the variables so the quiz starts disabled.
handler.reset_quiz()

if __name__ == "__main__":
    root.mainloop()
