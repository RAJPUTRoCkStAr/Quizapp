import subprocess #to make exe file work with this project
subprocess.run("install_dependencies.bat", shell=True)
import fitz  # PyMuPDF
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MCQ Quiz App")
        self.root.geometry("600x600")
        self.root.configure(bg="#f0f0f0")

        # Frame for uploading the PDF
        self.upload_frame = tk.Frame(root, bg="#f0f0f0")
        self.upload_frame.pack(pady=20)

        # Upload button
        self.upload_button = ttk.Button(self.upload_frame, text="Upload PDF", command=self.upload_file,width=30)
        self.upload_button.pack(pady=5)

        # Frame for displaying the quiz
        self.quiz_frame = tk.Frame(root, bg="#f0f0f0", borderwidth=2, relief="groove")
        self.quiz_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Question label
        self.question_label = tk.Label(self.quiz_frame, text="", wraplength=550, bg="#f0f0f0", font=("Arial", 14, "bold"))
        self.question_label.pack(pady=10)

        # Options frame
        self.options_frame = tk.Frame(self.quiz_frame, bg="#f0f0f0")
        self.options_frame.pack(pady=10)

        # Options radio buttons
        self.selected_answer = tk.StringVar(value="")  # Variable to store selected option

        self.option_a = ttk.Radiobutton(self.options_frame, text="", variable=self.selected_answer, value="A")
        self.option_b = ttk.Radiobutton(self.options_frame, text="", variable=self.selected_answer, value="B")
        self.option_c = ttk.Radiobutton(self.options_frame, text="", variable=self.selected_answer, value="C")
        self.option_d = ttk.Radiobutton(self.options_frame, text="", variable=self.selected_answer, value="D")

        self.option_a.pack(anchor="w", pady=5)
        self.option_b.pack(anchor="w", pady=5)
        self.option_c.pack(anchor="w", pady=5)
        self.option_d.pack(anchor="w", pady=5)

        # Submit button
        self.submit_button = ttk.Button(root, text="Submit Answer", command=self.submit_answer,width=30)
        self.submit_button.pack(pady=5)

        # Feedback label
        self.feedback_label = tk.Label(root, text="", bg="#f0f0f0", font=("Arial", 12, "bold"))
        self.feedback_label.pack(pady=5)

        # Next question button
        self.next_button = ttk.Button(root, text="Next Question", command=self.next_question,width=30)
        self.next_button.pack(pady=5)
        self.next_button.config(state=tk.DISABLED)  # Disabled by default until an answer is submitted

        # Show results button
        self.show_results_button = ttk.Button(root, text="Show Results", command=self.show_results,width=30)
        self.show_results_button.pack(pady=5)
        self.show_results_button.config(state=tk.DISABLED)  # Disabled until the quiz is finished

        # Quiz state variables
        self.correct_count = 0
        self.wrong_count = 0
        self.qa_pairs = []
        self.user_answers = []  # List to store user answers
        self.current_question_num = 0

    def upload_file(self):
        """Handle file upload"""
        pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if pdf_path:
            self.qa_pairs = self.extract_questions_answers(pdf_path)
            self.current_question_num = 0
            self.correct_count = 0
            self.wrong_count = 0
            self.user_answers = []  # Reset user answers
            self.show_question()

    def extract_questions_answers(self, pdf_path):
        """Extract questions and answers from the PDF"""
        doc = fitz.open(pdf_path)
        all_text = ""

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            all_text += page.get_text()

        # Regex pattern to match questions, options, and answers
        question_pattern = r'(\d+)\.\s(.+?)(A\..+?D\..+?)(ANSWER:\s[A-Z])'
        matches = re.findall(question_pattern, all_text, re.DOTALL)

        qa_pairs = []

        for match in matches:
            question_number = match[0]
            question_text = match[1].strip()
            options = match[2].strip()
            answer = match[3].replace("ANSWER: ", "").strip()

            qa_pairs.append({
                "Question": f"Q{question_number}: {question_text}",
                "Options": options,
                "Answer": answer
            })

        return qa_pairs

    def show_question(self):
        """Display the current question and options"""
        if self.current_question_num < len(self.qa_pairs):
            question = self.qa_pairs[self.current_question_num]
            self.question_label.config(text=question['Question'])

            # Extracting the options and updating radio button text
            options = question['Options'].split("\n")
            self.option_a.config(text=options[0])
            self.option_b.config(text=options[1])
            self.option_c.config(text=options[2])
            self.option_d.config(text=options[3])

            self.selected_answer.set("")  # Reset selected option
            self.feedback_label.config(text="")  # Clear feedback
            self.next_button.config(state=tk.DISABLED)  # Disable next button until answer is submitted
            self.show_results_button.config(state=tk.DISABLED)  # Disable show results button until the quiz is finished
        else:
            self.show_final_results()

    def submit_answer(self):
        """Check the selected answer and give feedback"""
        user_answer = self.selected_answer.get()
        correct_answer = self.qa_pairs[self.current_question_num]['Answer']

        # Store the user's answer
        self.user_answers.append({
            "Question": self.qa_pairs[self.current_question_num]['Question'],
            "User Answer": user_answer,
            "Correct Answer": correct_answer,
            "Is Correct": user_answer == correct_answer
        })

        if user_answer == correct_answer:
            self.feedback_label.config(text="Correct!", fg="green")
            self.correct_count += 1
        else:
            self.feedback_label.config(text=f"Wrong! The correct answer is: {correct_answer}", fg="red")
            self.wrong_count += 1

        # Enable next question button after submitting answer
        self.next_button.config(state=tk.NORMAL)
        self.submit_button.config(state=tk.DISABLED)  # Disable submit until the next question

        # Enable the show results button after every 10 questions
        if (self.current_question_num + 1) % 10 == 0:
            self.show_results_button.config(state=tk.NORMAL)

    def next_question(self):
        """Move to the next question"""
        self.current_question_num += 1
        self.show_question()

        # Enable submit and disable next until next answer
        self.submit_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.DISABLED)

    def show_final_results(self):
        """Display the final results when quiz is finished"""
        result_message = f"Quiz finished! Correct: {self.correct_count}, Wrong: {self.wrong_count}"
        messagebox.showinfo("Quiz Finished", result_message)
        self.show_results_button.config(state=tk.NORMAL)  # Enable the show results button
        self.submit_button.config(state=tk.DISABLED)  # Disable submit until the next question
        self.next_button.config(state=tk.DISABLED)  # Disable next until the quiz is finished
        self.root.quit()

    def show_results(self):
        """Show detailed results of each question"""
        result_window = tk.Toplevel(self.root)
        result_window.title("Detailed Results")
        result_window.geometry("500x500")
        result_window.configure(bg="#f7f7f7")

        # Frame for results
        results_frame = tk.Frame(result_window, bg="#f7f7f7")
        results_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Header label
        header_label = tk.Label(results_frame, text="Quiz Results", bg="#f7f7f7", font=("Arial", 16, "bold"))
        header_label.pack(pady=10)

        # Create a canvas for scrolling
        canvas = tk.Canvas(results_frame, bg="#f7f7f7")
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        results_content = tk.Frame(canvas, bg="#f7f7f7")

        results_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=results_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Display results
        for answer in self.user_answers:
            question_label = tk.Label(results_content, text=answer['Question'], bg="#f7f7f7", font=("Arial", 12, "bold"))
            question_label.pack(anchor="w", pady=2)

            user_answer_label = tk.Label(results_content, text=f"Your Answer: {answer['User Answer']}", bg="#f7f7f7", font=("Arial", 12))
            user_answer_label.pack(anchor="w", pady=2)

            correct_answer_label = tk.Label(results_content, text=f"Correct Answer: {answer['Correct Answer']}", bg="#f7f7f7", font=("Arial", 12))
            correct_answer_label.pack(anchor="w", pady=2)

            status_label = tk.Label(results_content, text="Status: " + ("Correct" if answer['Is Correct'] else "Wrong"), 
                                    bg="#f7f7f7", 
                                    font=("Arial", 12, "italic"),
                                    fg="green" if answer['Is Correct'] else "red")
            status_label.pack(anchor="w", pady=5)

            # Add a separator
            separator = ttk.Separator(results_content, orient="horizontal")
            separator.pack(fill="x", pady=5)

        # Add a close button
        close_button = ttk.Button(results_frame, text="Close", command=result_window.destroy,width=30)
        close_button.pack(pady=5)



if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
