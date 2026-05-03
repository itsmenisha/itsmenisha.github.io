from flask import Flask, render_template, request, session, redirect, url_for
import csv
import random
import os
import time

app = Flask(__name__)
app.secret_key = "wordle_secret_key"

EASY_WORDS = []
HARD_WORDS = []
CSV_FILE = "wordsforwordle.csv"


# ---------------- LOAD WORDS ----------------
def load_words():
    global EASY_WORDS, HARD_WORDS
    EASY_WORDS.clear()
    HARD_WORDS.clear()

    if not os.path.exists(CSV_FILE):
        print("CSV missing")
        return

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) < 2:
                continue

            word = row[0].strip().lower()
            diff = row[1].strip()

            if diff == "4":
                EASY_WORDS.append(word)
            elif diff == "5":
                HARD_WORDS.append(word)

    print("Loaded EASY:", len(EASY_WORDS), "HARD:", len(HARD_WORDS))


load_words()


# ---------------- WORD PICK ----------------
def get_word():
    mode = session.get("mode", "easy")
    pool = EASY_WORDS if mode == "easy" else HARD_WORDS
    return random.choice(pool) if pool else "test"


# ---------------- INIT GAME ----------------
def init_game():
    session["word"] = get_word()
    session["guesses"] = []
    session["status"] = "idle"
    session["start_time"] = None
    session["keyboard"] = {}


# ---------------- SCORING ----------------
def score_guess(word, guess):
    word_list = list(word)
    result = ["wrong"] * len(guess)

    for i in range(len(guess)):
        if guess[i] == word_list[i]:
            result[i] = "correct"
            word_list[i] = None

    for i in range(len(guess)):
        if result[i] == "correct":
            continue
        if guess[i] in word_list:
            result[i] = "present"
            word_list[word_list.index(guess[i])] = None

    return result


# ---------------- GRID ----------------
def build_grid(word, guesses):
    grid = []

    for i in range(6):
        if i < len(guesses):
            g = guesses[i]
            colors = score_guess(word, g)
            grid.append(list(zip(colors, g)))
        else:
            grid.append([("empty", "") for _ in word])

    return grid


# ---------------- KEYBOARD ----------------
def update_keyboard(kb, guess, colors):
    for ch, c in zip(guess, colors):
        if kb.get(ch) == "correct":
            continue
        if kb.get(ch) == "present" and c == "wrong":
            continue
        kb[ch] = c
    return kb


# ================= ROUTES =================

# HOME → ALWAYS WORDLE
@app.route("/")
def index():
    return redirect(url_for("wordle"))


@app.route("/wordle")
def wordle():
    if "word" not in session:
        init_game()

    word = session["word"]
    guesses = session.get("guesses", [])

    if guesses and guesses[-1] == word:
        status = "won"
    elif len(guesses) >= 6:
        status = "lost"
    elif guesses:
        status = "playing"
    else:
        status = "idle"

    session["status"] = status

    return render_template(
        "wordle.html",
        grid=build_grid(word, guesses),
        status=status,
        mode=session.get("mode", "easy"),
        length=len(word),
        keyboard=session.get("keyboard", {}),
        word=word,
        start_time=session.get("start_time")
    )


@app.route("/guess", methods=["POST"])
def guess():
    if session.get("status") in ["won", "lost"]:
        return redirect(url_for("wordle"))

    word = session["word"]
    g = request.form["guess"].lower().strip()

    if len(g) != len(word):
        return redirect(url_for("wordle"))

    if session.get("start_time") is None:
        session["start_time"] = time.time()

    session.setdefault("guesses", [])

    if len(session["guesses"]) < 6:
        session["guesses"].append(g)

        colors = score_guess(word, g)
        session["keyboard"] = update_keyboard(
            session.get("keyboard", {}), g, colors
        )

    return redirect(url_for("wordle"))


@app.route("/reset")
def reset():
    init_game()
    return redirect(url_for("wordle"))


@app.route("/mode/<mode>")
def mode(mode):
    if mode in ["easy", "hard"]:
        session["mode"] = mode
    init_game()
    return redirect(url_for("wordle"))


if __name__ == "__main__":
    load_words()
    app.run(debug=True)
