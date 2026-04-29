#!/usr/bin/env python3
"""
Worksheet Generator — Mogi Automation OS
Generates custom maths/science worksheet PDFs with answer keys.

Usage:
    python worksheet_generator.py --topic algebra --year 9 --questions 20 --output worksheet.pdf
    python worksheet_generator.py --topic trigonometry --year 10 --questions 15 --output trig_pack.pdf

Modes:
    --topic algebra      → Linear equations, factorisation, expansion
    --topic trigonometry  → SOH CAH TOA, sine/cosine rules, bearings
    --topic quadratics   → Expanding, factorising, quadratic formula
    --topic statistics   → Mean/median/mode, box plots, probability
"""

import argparse
import os
import random
import sys
import math


# ── Question Generators ────────────────────────────────────────────────────


def gen_algebra_q(difficulty=1):
    """Generate an algebra question at a given difficulty level (1-3)."""
    a = random.randint(2, 10)
    b = random.randint(1, 20)
    c = random.randint(1, 10)
    x = random.randint(-10, 10)

    if difficulty == 1:
        # Simple linear: ax + b = c
        x = (c - b) / a
        if x != int(x):
            return gen_algebra_q(difficulty)
        q = f"Solve for x: {a}x + {b} = {c}"
        a = int(x)
        return q, int(x)
    elif difficulty == 2:
        # ax + b = cx + d
        c = random.randint(1, a - 1) if a > 1 else random.randint(1, 5)
        d = random.randint(1, 15)
        x_num = d - b
        x_den = a - c
        if x_den == 0 or x_num % x_den != 0:
            return gen_algebra_q(difficulty)
        x = x_num // x_den
        q = f"Solve for x: {a}x + {b} = {c}x + {d}"
        return q, x
    else:
        # Expand: (ax + b)(cx + d)
        c = random.randint(1, 5)
        d = random.randint(-10, 10)
        ac = a * c
        adbc = a * d + b * c
        bd = b * d
        signs_adbc = "+" if adbc >= 0 else ""
        signs_bd = "+" if bd >= 0 else ""
        q = f"Expand: ({a}x {'+' if b >= 0 else '-'} {abs(b)})({c}x {'+' if d >= 0 else '-'} {abs(d)})"
        a_str = f"{ac}x²" if ac != 1 else "x²"
        mid_str = f"{signs_adbc}{adbc}x" if adbc != 0 else ""
        end_str = f" {signs_bd}{bd}" if bd != 0 else ""
        answer = f"{a_str} {mid_str}{end_str}".strip()
        answer = " ".join(answer.split())
        return q, answer


def gen_trig_q(difficulty=1):
    """Generate a trigonometry question."""
    angle = random.choice([30, 45, 60, 15, 75])
    side1 = random.randint(3, 15)
    
    if difficulty == 1:
        # SOH CAH TOA find side
        trig = random.choice(["sin", "cos", "tan"])
        q = f"In a right-angled triangle, angle = {angle}°, adjacent = {side1}. Find the opposite side (to 2 dp)."
        if trig == "sin":
            # opposite = tan(angle) * adjacent
            ans = round(math.tan(math.radians(angle)) * side1, 2)
        else:
            ans = round(math.sin(math.radians(angle)) * side1, 2) if trig == "sin" else round(math.cos(math.radians(angle)) * side1, 2)
        return q, ans
    elif difficulty == 2:
        # Find angle from sides, any triangle
        sides_a = random.randint(5, 15)
        sides_b = random.randint(5, 15)
        angle_c = random.randint(30, 120)
        c2 = sides_a**2 + sides_b**2 - 2 * sides_a * sides_b * math.cos(math.radians(angle_c))
        side_c = round(math.sqrt(c2), 2)
        q = f"In a triangle, side a = {sides_a}cm, side b = {sides_b}cm, angle C = {angle_c}°. Find side c (to 2 dp)."
        return q, side_c
    else:
        # Sine rule
        q_a = random.randint(20, 70)
        q_b = random.randint(20, 70)
        if q_a + q_b >= 180:
            return gen_trig_q(difficulty)
        side_c = random.randint(5, 20)
        # side_b / sin(B) = side_c / sin(C)
        angle_c = 180 - q_a - q_b
        sin_a = math.sin(math.radians(q_a))
        sin_c = math.sin(math.radians(angle_c))
        side_a = round(side_c * sin_a / sin_c, 2)
        q = f"In triangle ABC, angle A = {q_a}°, angle B = {q_b}°, side c = {side_c}cm. Find side a (to 2 dp)."
        return q, side_a


TOPICS = {
    "algebra": gen_algebra_q,
    "trigonometry": gen_trig_q,
    # More topics can be added as modules
}


def generate_worksheet(topic, year, num_questions, output_path):
    """Generate a complete worksheet and answer key."""
    if topic not in TOPICS:
        print(f"❌ Unknown topic: {topic}")
        print(f"   Available: {', '.join(TOPICS.keys())}")
        sys.exit(1)

    generator = TOPICS[topic]
    questions = []
    answers = []

    # Determine difficulty based on year
    if year <= 8:
        max_diff = 1
    elif year <= 10:
        max_diff = 2
    else:
        max_diff = 3

    for i in range(num_questions):
        diff = random.randint(1, max_diff)
        try:
            q, a = generator(diff)
        except (RecursionError, TypeError):
            q, a = generator(1)
        questions.append((i + 1, q))
        answers.append((i + 1, a))

    file_ext = os.path.splitext(output_path)[1].lower()

    if file_ext == ".txt":
        output_text(questions, answers, topic, year, output_path)
    elif file_ext == ".md":
        output_markdown(questions, answers, topic, year, output_path)
    elif file_ext == ".tex":
        output_latex(questions, answers, topic, year, output_path)
    else:
        # Default to text
        output_path += ".txt"
        output_text(questions, answers, topic, year, output_path)

    print(f"✅ Worksheet generated: {output_path}")


def output_text(questions, answers, topic, year, path):
    with open(path, "w") as f:
        f.write(f"{topic.title()} Worksheet — Year {year}\n")
        f.write("=" * 50 + "\n\n")
        f.write("Name: _______________  Date: _______________\n\n")
        f.write("-" * 50 + "\n\n")
        for num, q in questions:
            f.write(f"{num}. {q}\n\n")
        f.write("\n" + "=" * 50 + "\n")
        f.write("ANSWER KEY\n")
        f.write("=" * 50 + "\n\n")
        for num, a in answers:
            f.write(f"{num}. {a}\n")


def output_markdown(questions, answers, topic, year, path):
    with open(path, "w") as f:
        f.write(f"# {topic.title()} Worksheet — Year {year}\n\n")
        f.write("Name: _______________ | Date: _______________\n\n")
        f.write("---\n\n")
        for num, q in questions:
            f.write(f"**{num}.** {q}\n\n")
        f.write("\n---\n\n# Answer Key\n\n")
        for num, a in answers:
            f.write(f"**{num}.** {a}\n")


def output_latex(questions, answers, topic, year, path):
    with open(path, "w") as f:
        f.write("\\documentclass[12pt]{article}\n")
        f.write("\\usepackage[a4paper,margin=2cm]{geometry}\n")
        f.write("\\usepackage{amsmath}\n")
        f.write(f"\\title{{{topic.title()} Worksheet — Year {year}}}\n")
        f.write("\\begin{document}\n")
        f.write("\\maketitle\n\n")
        f.write("\\textbf{Name: \\hrulefill \\hspace{2cm} Date: \\hrulefill}\n\n")
        for num, q in questions:
            f.write(f"\\textbf{{{num}.}} {q}\n\n")
        f.write("\\newpage\n")
        f.write("\\section*{Answer Key}\n")
        for num, a in answers:
            f.write(f"\\textbf{{{num}.}} {a}\n\n")
        f.write("\\end{document}")


def main():
    parser = argparse.ArgumentParser(description="Generate maths/science worksheet with answer key.")
    parser.add_argument("--topic", "-t", required=True, choices=list(TOPICS.keys()), help="Topic")
    parser.add_argument("--year", "-y", type=int, required=True, help="Year level (7-12)")
    parser.add_argument("--questions", "-q", type=int, default=20, help="Number of questions")
    parser.add_argument("--output", "-o", default="worksheet.txt", help="Output file (.txt, .md, .tex)")
    args = parser.parse_args()

    generate_worksheet(args.topic, args.year, args.questions, args.output)


if __name__ == "__main__":
    main()
