import random
import sqlite3
import os
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
if os.environ.get("VERCEL"):
  DB_NAME = "/tmp/database.db"
else:
  DB_NAME = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Questions Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter TEXT NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL
        )
    """)

    # Users Table (Unique Mat No)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            mat_no TEXT UNIQUE NOT NULL
        )
    """)

    # Assessments History Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            raw_score INTEGER NOT NULL,
            score_over_70 REAL NOT NULL,
            percentage REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Populate questions if empty
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] == 0:
        seed_questions(cursor)

    conn.commit()
    conn.close()

def seed_questions(cursor):
    """Seed the database with all 118 textbook questions."""
    sample_dataset = [
        # --- CHAPTER 1 ---
        ("Chapter 1", "Which of the following is considered an input device?", "Monitor", "Printer", "Microphone", "Speakers", "C"),
        ("Chapter 1", "What is the primary function of the CPU?", "Storing long-term data", "Executing instructions and performing calculations", "Displaying output to the user", "Connecting all hardware components", "B"),
        ("Chapter 1", "RAM is a type of memory that is volatile, which means:", "It is used for long-term storage.", "It is slower than secondary storage.", "Its data is lost when the power is turned off.", "It can only be read, not written to.", "C"),
        ("Chapter 1", "A program designed to perform a specific task for the user, such as a word processor or a web browser, is known as:", "System software", "Application software", "Firmware", "A device driver", "B"),
        ("Chapter 1", "What is the main difference between a compiled and an interpreted language?", "Compiled languages are more flexible.", "Interpreted languages are faster.", "Compiled languages are fully translated to machine code before execution.", "Interpreted languages are closer to hardware.", "C"),
        ("Chapter 1", "Which of these is a key principle of Object-Oriented Programming (OOP)?", "Focusing on a sequence of instructions.", "Treating computation as the evaluation of mathematical functions.", "Organizing code around objects with data and methods.", "Writing programs as a set of facts and rules.", "C"),
        ("Chapter 1", "The motherboard is responsible for:", "Providing power to the computer.", "Performing arithmetic operations.", "Connecting all major hardware components.", "Running the operating system.", "C"),
        ("Chapter 1", "What is the purpose of a device driver?", "To manage the computer's memory.", "To provide a user interface.", "To allow the operating system to communicate with a specific hardware component.", "To translate human-readable code into machine code.", "C"),
        ("Chapter 1", "Which of the following is a low-level language?", "Python", "Java", "Assembly", "C++", "C"),
        ("Chapter 1", "The ethical principle of intellectual property primarily addresses:", "Protecting personal data.", "Avoiding cyberbullying.", "Respecting copyrights and avoiding piracy.", "Using technology for social good.", "C"),

        # --- CHAPTER 2 ---
        ("Chapter 2", "Which of the following is an example of an output device?", "Keyboard", "Scanner", "Printer", "Mouse", "C"),
        ("Chapter 2", "The 'brain' of the computer that executes instructions is the:", "RAM", "CPU", "Motherboard", "Hard Drive", "B"),
        ("Chapter 2", "What is the primary difference between a manual method and a computer method of data processing?", "The manual method is more reliable.", "The computer method is slower.", "The computer method is more accurate and efficient.", "The manual method can process larger volumes of data.", "C"),
        ("Chapter 2", "The concept that allows a computer to store both data and instructions in its memory is known as the:", "CPU principle", "Stored program concept", "Input-Process-Output model", "Parallel processing", "B"),
        ("Chapter 2", "Which programming language was developed during the fourth generation of computers and is still widely used today?", "FORTRAN", "COBOL", "C", "BCPL", "C"),
        ("Chapter 2", "An algorithm is best described as:", "A type of hardware component.", "A step-by-step procedure for solving a problem.", "A type of operating system.", "A program that runs on a computer.", "B"),
        ("Chapter 2", "Which generation of computers was characterized by the use of integrated circuits?", "First Generation", "Second Generation", "Third Generation", "Fourth Generation", "C"),
        ("Chapter 2", "A person who uses a computer primarily for graphic design and video editing would be categorized as a:", "Casual user", "Beginner", "Creative Professional", "Gamer", "C"),
        ("Chapter 2", "What is the main function of the Operating System (OS)?", "To run specific user tasks.", "To store data long-term.", "To manage hardware resources and provide a platform for applications.", "To connect computers via a network.", "C"),
        ("Chapter 2", "The development of the transistor was the key technological advancement of which computer generation?", "First Generation", "Second Generation", "Third Generation", "Fourth Generation", "B"),

        # --- CHAPTER 3 ---
        ("Chapter 3", "Which of the following is NOT a characteristic of a well-defined problem?", "Clear goals", "Specific procedures", "Predictable outcomes", "Subjective interpretation", "D"),
        ("Chapter 3", "Which problem type typically involves unpredictable variables and multiple disciplines?", "Routine Problem", "Complex Problem", "Well-defined Problem", "Ill-defined Problem", "D"),
        ("Chapter 3", "What is the first step in defining a problem effectively?", "Identify constraints", "Clarify the problem statement", "Frame the problem", "Define success metrics", "B"),
        ("Chapter 3", "Which characteristic of a problem is best exemplified by a software team having a limited budget and a strict deadline to complete a project?", "Existence of a Goal", "Difference Between Actual and Desired State", "Uncertainty", "Resource Constraints", "D"),
        ("Chapter 3", "An individual encounters a situation they have solved many times before and applies a standard procedure to find the solution. According to the text, what type of problem is this?", "Novel problem", "Ill-defined problem", "Routine problem", "Complex problem", "C"),
        ("Chapter 3", "What is the primary distinction between a well-defined problem and an ill-defined problem?", "Well-defined problems are always easier.", "Ill-defined problems have clear parameters.", "Well-defined problems have clear goals and rules, while ill-defined problems lack this clarity.", "Well-defined problems require creative thinking.", "C"),
        ("Chapter 3", "According to the chapter, which of the following is a key strategy for effective problem definition?", "Ignoring all uncertainties to simplify the problem.", "Relying on initial assumptions without gathering more information.", "Clearly framing the problem by asking 'what', 'why', and 'how'.", "Only identifying one possible solution to focus the effort.", "C"),
        ("Chapter 3", "The term 'problem domain' is best described as:", "A specific programming language used.", "A list of all possible solutions to a problem.", "The collection of knowledge, context, and constraints related to a problem.", "A complex problem that is difficult to solve.", "C"),
        ("Chapter 3", "A student is asked to solve a math problem that requires them to apply the Pythagorean theorem. According to the chapter, this would be an example of a:", "Non-routine problem", "Novel problem", "Ill-defined problem", "Routine problem", "D"),
        ("Chapter 3", "The process of 'Guess and check' is cited as a useful strategy for which of the following problems?", "The sum of numbers from 1 to N.", "A problem requiring the calculation of a specific number.", "Placing numbers 1 to 9 in a triangle to sum to 20.", "Finding the sum of a series of numbers given by family members.", "C"),
        ("Chapter 3", "What does the text identify as the 'gap' that defines the existence of a problem?", "The gap between one's current skills and the skills needed.", "The difference between the actual state and the desired state.", "The gap in available resources like time and finances.", "The gap between an algorithm and a creative solution.", "B"),
        ("Chapter 3", "When comparing routine and non-routine problems, which feature is associated with a high cognitive demand?", "Following a standard procedure or algorithm.", "An unfamiliar and new context.", "A clear and specific goal.", "Reinforcing fluency and procedural understanding.", "B"),
        ("Chapter 3", "A problem that is unstructured and involves ambiguous constraints and vague goals is most likely a:", "Complex problem", "Well-defined problem", "Routine problem", "Novel problem", "A"),

        # --- CHAPTER 4 ---
        ("Chapter 4", "Which algorithm has O(n log n) time complexity?", "Bubble Sort", "Merge Sort", "Linear Search", "Quick Sort", "B"),
        ("Chapter 4", "What does O(1) represent in Big-O notation?", "Linear time", "Constant time", "Quadratic time", "Exponential time", "B"),
        ("Chapter 4", "Which search algorithm requires a sorted input?", "Linear Search", "Binary Search", "Depth-First Search", "Breadth-First Search", "B"),
        ("Chapter 4", "Hill Climbing can get stuck in:", "Global maxima", "Local maxima", "Infinite loops", "Syntax errors", "B"),
        ("Chapter 4", "Which is a heuristic method?", "Binary Search", "Hill Climbing", "Merge Sort", "Quick Sort", "B"),
        ("Chapter 4", "The Traveling Salesman Problem is:", "NP-complete", "Solvable in O(n) time", "Solvable in O(1) time", "Undecidable", "A"),
        ("Chapter 4", "Which is the best time complexity?", "O(n²)", "O(1)", "O(2^n)", "O(n)", "B"),
        ("Chapter 4", "A* algorithm is used for:", "Sorting", "Pathfinding", "Hashing", "Searching", "B"),
        ("Chapter 4", "Simulated Annealing helps in:", "Escaping local optima", "Exact shortest path", "Generating random numbers", "Sorting arrays", "A"),
        ("Chapter 4", "Genetic Algorithms are inspired by:", "Physics", "Evolution", "Chemistry", "Mathematics", "B"),

        # --- CHAPTER 5 ---
        ("Chapter 5", "Which problem is a canonical example of a non-solvable (undecidable) problem?", "Sorting a list of integers", "Finding the shortest path in a graph", "The Halting Problem", "Solving a linear equation", "C"),
        ("Chapter 5", "A problem is 'solvable' if:", "It can be solved efficiently (in polynomial time).", "An algorithm exists that correctly solves it for all inputs in finite time.", "It can be approximated using heuristics.", "Humans can intuitively solve it.", "B"),
        ("Chapter 5", "Which statement about non-solvable problems is TRUE?", "They can be solved if given enough computational resources.", "They are exclusively found in theoretical mathematics.", "They have no algorithm that works for all inputs.", "They are equivalent to NP-hard problems.", "C"),
        ("Chapter 5", "The class of solvable problems is:", "Closed under complement (if a problem is solvable, so is its complement).", "Limited to problems in class P.", "Smaller than the set of non-solvable problems.", "Only applicable to deterministic systems.", "A"),
        ("Chapter 5", "A problem is non-solvable in a formal system if:", "It is NP-complete.", "It reduces to the Halting Problem.", "It requires exponential time.", "It involves continuous variables.", "B"),

        # --- CHAPTER 6 ---
        ("Chapter 6", "Which problem-solving technique involves hiding complex details to focus on high-level mechanisms?", "Means-End Analysis", "Trial and Error", "Abstraction", "Hypothesis Testing", "C"),
        ("Chapter 6", "In the context of problem-solving, what is a 'heuristic'?", "A proven, guaranteed algorithm", "A rule of thumb or a mental shortcut", "A complex mathematical formula", "A method that requires no prior knowledge", "B"),
        ("Chapter 6", "The process of generating a wide range of ideas in a short time, often without criticism, is known as:", "Hypothesis Testing", "Abstraction", "Reductionism", "Brainstorming", "D"),
        ("Chapter 6", "Which of the following is an example of a Type I Error in hypothesis testing?", "Failing to reject a false null hypothesis", "Rejecting a true null hypothesis", "Failing to reject a true null hypothesis", "Rejecting a false alternative hypothesis", "B"),
        ("Chapter 6", "When a computer programmer must write code with exact syntax and commands, they are using what kind of thinking?", "Abstract thinking", "Holistic thinking", "Literal thinking", "Analogical thinking", "C"),
        ("Chapter 6", "The SCAMPER technique is primarily used in which problem-solving method?", "Hypothesis Testing", "Trial and Error", "Means-End Analysis", "Brainstorming", "D"),
        ("Chapter 6", "The primary goal of Means-End Analysis (MEA) is to:", "Identify the best possible solution from a known set of options", "Break down a problem into a series of sub-goals", "Compare the current state with the goal state and reduce the difference", "Create new solutions by drawing parallels between concepts", "C"),
        ("Chapter 6", "A software developer uses an API to connect their application to a social media platform. This is a practical example of:", "Trial and Error", "Analogy", "Abstraction", "Literal Thinking", "C"),
        ("Chapter 6", "Which of these is a significant limitation of the trial-and-error approach?", "It requires a lot of prior knowledge.", "It is not suitable for simple problems.", "It can be time-consuming and inefficient.", "It is only useful in computer science.", "C"),
        ("Chapter 6", "If a scientist tests a new drug by assuming there is no difference in its effectiveness compared to an old drug, this initial assumption is called the:", "Alternative Hypothesis", "P-value", "Test Statistic", "Null Hypothesis", "D"),

        # --- CHAPTER 7 ---
        ("Chapter 7", "Which problem-solving method is a creative technique that involves combining the attributes of an unrelated object with a problem?", "Root Cause Analysis", "Morphological Analysis", "Method of Focal Objects", "Divide and Conquer", "C"),
        ("Chapter 7", "What is the main purpose of Root Cause Analysis (RCA)?", "To blame individuals for errors.", "To treat the symptoms of a problem.", "To identify the underlying reasons a problem occurred.", "To generate as many solutions as possible.", "C"),
        ("Chapter 7", "The 5 Whys technique and a Fishbone Diagram are tools used in which problem-solving method?", "Morphological Analysis", "Root Cause Analysis", "Method of Focal Objects", "Proof and Validation", "B"),
        ("Chapter 7", "A company is redesigning a vehicle. They list parameters like 'Power Source' and 'Terrain' and then explore all possible combinations. What method are they using?", "Morphological Analysis", "Divide and Conquer", "Method of Focal Objects", "Root Cause Analysis", "A"),
        ("Chapter 7", "What is the primary difference between Proof and Validation?", "Proof is for software, while Validation is for hardware.", "Proof is about real-world effectiveness, while Validation is about logical certainty.", "Proof is about logical certainty, while Validation is about real-world relevance.", "Proof and Validation are two terms for the same process.", "C"),
        ("Chapter 7", "The Divide and Conquer strategy is best described by which three stages?", "Define, Identify, and Analyse", "Divide, Conquer, and Combine", "Research, Test, and Implement", "Brainstorm, Refine, and Evaluate", "B"),
        ("Chapter 7", "Which of the following is a disadvantage of the Divide and Conquer strategy?", "It is not efficient for large datasets.", "It prevents problems from being solved in parallel.", "It can lead to recursion overhead and excessive memory use.", "It is only applicable to sorting algorithms.", "C"),
        ("Chapter 7", "In a Morphological Box, what do the rows and columns represent?", "Rows represent problems, and columns represent solutions.", "Rows represent parameters, and columns represent their possible values.", "Rows represent symptoms, and columns represent root causes.", "Rows represent pros, and columns represent cons.", "B"),
        ("Chapter 7", "A key principle of Root Cause Analysis is to focus on:", "The person responsible for the error.", "Finding a quick, temporary fix.", "Systems and processes, not blame.", "The most obvious cause of the problem.", "C"),
        ("Chapter 7", "When a software team performs Unit Testing and User Acceptance Testing (UAT), they are primarily engaged in which part of the problem-solving process?", "Root Cause Analysis", "Validation", "Proof by Contradiction", "Morphological Analysis", "B"),

        # --- CHAPTER 8 ---
        ("Chapter 8", "What is the primary goal of the Planning and Designing stage?", "To write clean and readable code.", "To outline the steps and logic of the solution before coding.", "To fix bugs in the program.", "To add comments to the code.", "B"),
        ("Chapter 8", "In which stage would you create a flowchart or pseudocode?", "Understanding the Problem", "Planning and Designing", "Implementing the Solution", "Evaluating and Refining", "B"),
        ("Chapter 8", "Testing for edge cases is a key activity in which stage?", "Implementation", "Planning", "Evaluation and Refining", "Documentation", "C"),
        ("Chapter 8", "The final stage of the problem-solving process is to:", "Find the fastest algorithm.", "Document and communicate the solution.", "Start a new project.", "Get user feedback.", "B"),
        ("Chapter 8", "What is the main purpose of adding comments to your code?", "To make the program run faster.", "To make the code look more professional.", "To help explain the code's purpose and logic to humans.", "To remove the need for functions.", "C"),
        ("Chapter 8", "An algorithm is best defined as:", "A visual representation of a program's logic.", "A specific programming language.", "A reusable block of code.", "A set of step-by-step instructions to solve a problem.", "D"),
        ("Chapter 8", "Which of the following is an example of an input for a program that calculates the average of three numbers?", "The calculated average.", "A print statement.", "The three numbers themselves.", "The name of the program.", "C"),
        ("Chapter 8", "What is the main goal of the evaluation stage in problem solving?", "To document the solution.", "To plan the algorithm.", "To verify correctness and optimize performance.", "To gather user input.", "C"),
        ("Chapter 8", "The implementation stage involves ___ the solution using a programming language.", "Planning", "Designing", "Evaluating", "Translating/coding", "D"),
        ("Chapter 8", "Why is it important to understand the constraints of a problem before designing a solution?", "Constraints are not important in the planning stage.", "They may influence the choice of algorithm and data structures.", "They are only relevant during the implementation stage.", "They help in documenting the solution later.", "B"),

        # --- CHAPTER 9 ---
        ("Chapter 9", "Which of the following activities is primarily associated with the Solution Formulation phase?", "Writing detailed class specifications.", "Gathering functional and non-functional requirements.", "Implementing a database schema.", "Writing unit tests for specific functions.", "B"),
        ("Chapter 9", "What is the purpose of a Feasibility Matrix?", "To list all possible solutions.", "To score the team's technical skills.", "To evaluate potential solutions based on technical, economic, and operational factors.", "To assign tasks to team members.", "C"),
        ("Chapter 9", "The main difference between High-Level Design (HLD) and Low-Level Design (LLD) is that:", "HLD uses Python, while LLD uses other languages.", "HLD focuses on detailed functions, while LLD focuses on architecture.", "HLD focuses on the system's overall architecture, while LLD focuses on granular component details.", "HLD is for small projects, and LLD is for large projects.", "C"),
        ("Chapter 9", "Which of the following is a non-functional requirement?", "The system must process user payments.", "The system must allow users to reset their passwords.", "The system must generate a PDF report.", "The system must handle 100 concurrent users with a response time of less than 2 seconds.", "D"),
        ("Chapter 9", "What is the role of pseudocode in the solution design process?", "To replace the need for writing actual code.", "To describe an algorithm's logic in plain language before coding.", "To generate an executable script.", "To create visual diagrams of the system.", "B"),
        ("Chapter 9", "In a flowchart, what does a diamond shape typically represent?", "A process or action.", "An input or output.", "The start or end of the process.", "A decision or conditional check.", "D"),
        ("Chapter 9", "When a developer uses a tool like pytest to verify if a function works as expected, they are primarily engaged in which part of the solution process?", "Problem Definition.", "Requirement Gathering.", "Validation.", "Feasibility Analysis.", "C"),
        ("Chapter 9", "Which Python library is best suited for conducting a feasibility check by measuring the memory usage of an object?", "pandas", "Matplotlib", "sys", "os", "C"),
        ("Chapter 9", "A developer uses Sphinx and MkDocs for a Python project. What activity are they most likely performing?", "Documentation.", "Unit Testing.", "Database management.", "Web development.", "A"),
        ("Chapter 9", "According to the chapter, why are flowcharts particularly valuable when working with Python?", "They are only used by data scientists.", "They replace the need for a database.", "They serve as a clear blueprint for Python's logical structures like loops and conditionals.", "They help in selecting the correct Python frameworks.", "C"),

        # --- CHAPTER 10 ---
        ("Chapter 10", "What is the purpose of a decision structure in a computer program?", "To store large data", "To perform repeated tasks", "To choose between actions based on conditions", "To display graphics", "C"),
        ("Chapter 10", "Which of the following is not a component of a decision table?", "Action Stub", "Rule", "Algorithm", "Condition Stub", "C"),
        ("Chapter 10", "A limited entry decision table contains:", "Only Yes/No or True/False values", "Numeric ranges only", "Multiple or infinite values", "No conditions", "A"),
        ("Chapter 10", "In Python, which keyword starts a decision structure?", "Loop", "Input", "if", "case", "C"),
        ("Chapter 10", "A decision tree is best described as:", "A database schema", "A graphical representation of decision logic", "A list of Python variables", "A structured loop", "B"),
        ("Chapter 10", "Which of these is a valid Python if condition?", "if x == 10:", "if x is 10 then", "if x >= 10:D", "if x == 10 then", "A"),
        ("Chapter 10", "A decision tree's terminal node represents:", "Another condition", "A branching point", "A final action or outcome", "A loop", "C"),
        ("Chapter 10", "An extended entry decision table allows:", "Only one action", "Only binary decisions", "Complex conditions such as ranges and inequalities", "Only single rules", "C"),
        ("Chapter 10", "The number of possible rules in a decision table with 3 binary conditions is:", "2", "4", "6", "8", "D"),
        ("Chapter 10", "What kind of Python statement is most suitable for implementing a decision tree?", "Loop", "Function", "Conditional (if, elif, else)", "List", "C"),

        # --- CHAPTER 11 ---
        ("Chapter 11", "What is the primary characteristic of Python as an interpreted language?", "It requires a separate compilation step before execution.", "It executes the source code line by line at runtime.", "It is only suitable for simple scripting.", "It must be run on a specific type of hardware.", "B"),
        ("Chapter 11", "Which of the following is a key feature that makes Python easy to learn and maintain?", "Its complex syntax with many keywords.", "Its use of indentation to define code blocks.", "Its support for manual memory management.", "Its need for explicit variable type declarations.", "B"),
        ("Chapter 11", "Which of these is an invalid Python identifier?", "my_variable", "_my_var", "2nd_variable", "MyVariable", "C"),
        ("Chapter 11", "A dictionary in Python stores data as:", "An ordered sequence of items.", "An immutable collection of unique elements.", "An unordered collection of key-value pairs.", "A mutable sequence of homogeneous elements.", "C"),
        ("Chapter 11", "What is the purpose of a comment in a Python program?", "To increase the execution speed.", "To perform a specific function or operation.", "To provide a human-readable explanation of the code that is ignored by the interpreter.", "To declare a new variable.", "C"),
        ("Chapter 11", "Which of the following data structures is immutable?", "List", "Dictionary", "Set", "Tuple", "D"),
        ("Chapter 11", "Which operator is used to perform string concatenation in Python?", "*", "=", "+", "()", "C"),
        ("Chapter 11", "What happens when you run the following code? set1 = {1, 2, 3}; set1.add([4, 5])", "The set becomes {1, 2, 3, 4, 5}.", "The set becomes {1, 2, 3, [4, 5]}.", "A TypeError is raised because a list is not hashable.", "The code runs without error, but the list is not added.", "C"),
        ("Chapter 11", "The Python Virtual Machine (PVM) is responsible for executing:", "The source code directly.", "The intermediate bytecode.", "The compiled machine code.", "A web browser.", "B"),
        ("Chapter 11", "Which statement is true about Python variables?", "You must declare the variable type before assigning a value.", "Variable types are determined automatically based on the assigned value.", "A variable can only be assigned a value once.", "Variable names can contain spaces.", "B"),

        # --- CHAPTER 12 ---
        ("Chapter 12", "What is a key benefit of Python being an interpreted language?", "It executes programs faster than compiled languages.", "It requires a separate compilation step.", "It allows for immediate feedback and easier debugging.", "It can only run on a single operating system.", "C"),
        ("Chapter 12", "Which of the following is an example of an invalid identifier in Python?", "my_age", "_name", "Age1", "if", "D"),
        ("Chapter 12", "What is the purpose of the if __name__ == '__main__': block?", "It defines a new function named main.", "It ensures that the code inside the block only runs when the script is executed directly.", "It marks the start of a new module.", "It is used to declare global variables.", "B"),
        ("Chapter 12", "Which of the following data types is always returned by the input() function?", "int", "float", "str", "bool", "C"),
        ("Chapter 12", "What is the recommended way to format strings in modern Python (3.6+)?", "The % operator.", "The + concatenation operator.", "The .format() method.", "f-strings.", "D"),
        ("Chapter 12", "Which of the following describes the behaviour of a for loop in Python?", "It repeats a block of code as long as a condition is true.", "It executes a block of code only once.", "It is used to define functions.", "It iterates over the items of a sequence or any other iterable.", "D"),
        ("Chapter 12", "A function that calls itself is known as a:", "Recursive function.", "Built-in function.", "Lambda function.", "Modular function.", "A"),
        ("Chapter 12", "What is the role of bytecode in Python's execution process?", "It is the final output of the program.", "It is an intermediate representation of the source code executed by the PVM.", "It is a human-readable form of the program.", "It is the raw source code itself.", "B"),
        ("Chapter 12", "Which of these is a benefit of modular programming?", "It makes all programs run on a single platform.", "It requires all code to be written in a single file.", "It makes code more reusable and easier to debug.", "It removes the need for functions.", "C"),
        ("Chapter 12", "In a function definition, def add(a, b):, what are a and b called?", "Arguments", "Variables", "Parameters", "Keywords", "C")
    ]

    cursor.executemany("""
        INSERT INTO questions (chapter, question_text, option_a, option_b, option_c, option_d, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_dataset)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/auth", methods=["POST"])
def auth():
    data = request.json
    name = data.get("name").strip()
    department = data.get("department").strip()
    mat_no = data.get("mat_no").strip().upper()

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name FROM users WHERE mat_no = ?", (mat_no,))
    user = cursor.fetchone()
    
    if user:
        user_id = user["id"]
        user_name = user["name"]
    else:
        cursor.execute("INSERT INTO users (name, department, mat_no) VALUES (?, ?, ?)", 
                       (name, department, mat_no))
        user_id = cursor.lastrowid
        user_name = name
        conn.commit()
        
    conn.close()
    return jsonify({"success": True, "user_id": user_id, "name": user_name, "mat_no": mat_no})

@app.route("/api/practice", methods=["GET"])
def get_practice_session():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, chapter, question_text, option_a, option_b, option_c, option_d FROM questions")
    all_questions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    random.shuffle(all_questions)
    selected_questions = all_questions[:35]

    return jsonify({"count": len(selected_questions), "questions": selected_questions})

@app.route("/api/submit", methods=["POST"])
def submit_practice():
    data = request.json
    user_answers = data.get("answers", {})
    user_id = data.get("user_id")

    if not user_answers or not user_id:
        return jsonify({"error": "Invalid submission"}), 400

    question_ids = list(user_answers.keys())
    placeholders = ",".join("?" for _ in question_ids)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT id, question_text, correct_answer, option_a, option_b, option_c, option_d 
        FROM questions WHERE id IN ({placeholders})
    """, question_ids)

    db_records = {str(row["id"]): dict(row) for row in cursor.fetchall()}
    
    score = 0
    results = []

    for q_id, user_choice in user_answers.items():
        record = db_records.get(str(q_id))
        if record:
            correct_choice = record["correct_answer"]
            is_correct = user_choice.upper() == correct_choice.upper()
            if is_correct:
                score += 1

            results.append({
                "question_text": record["question_text"],
                "user_choice": user_choice,
                "correct_choice": correct_choice,
                "is_correct": is_correct,
                "options": {"A": record["option_a"], "B": record["option_b"], "C": record["option_c"], "D": record["option_d"]}
            })

    total_submitted = len(user_answers)
    percentage = (score / total_submitted) * 100 if total_submitted > 0 else 0
    score_over_70 = (score / total_submitted) * 70 if total_submitted > 0 else 0

    cursor.execute("INSERT INTO assessments (user_id, raw_score, score_over_70, percentage) VALUES (?, ?, ?, ?)",
                   (user_id, score, score_over_70, percentage))
    conn.commit()
    conn.close()

    return jsonify({
        "score": score,
        "total": total_submitted,
        "percentage": round(percentage, 1),
        "score_over_70": round(score_over_70, 2),
        "details": results
    })

# --- NEW ENDPOINT TO FETCH HISTORY ---
@app.route("/api/history/<int:user_id>", methods=["GET"])
def get_history(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT raw_score, score_over_70, percentage, timestamp 
        FROM assessments 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    """, (user_id,))
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "history": history})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)