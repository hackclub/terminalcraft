import random
import time
import sys

# --- Email Samples (Realistic) ---
EMAIL_SAMPLES = [
    # Legitimate
    {
        "subject": "Your Amazon.com order has shipped",
        "sender": "shipment-tracking@amazon.com",
        "body": "Hello,\n\nYour order #123-4567890-1234567 has shipped. Track your package for the latest updates.\n\nThank you for shopping with us.",
        "attachments": [],
        "correct": "legit"
    },
    {
        "subject": "Your monthly bank statement is ready",
        "sender": "no-reply@yourbank.com",
        "body": "Dear Customer,\n\nYour monthly statement is now available. Please log in to your online banking account to view your statement securely.\n\nThank you,\nYourBank",
        "attachments": [],
        "correct": "legit"
    },
    {
        "subject": "Company All-Hands Meeting Tomorrow",
        "sender": "hr@company.com",
        "body": "Hi Team,\n\nThis is a reminder for our all-hands meeting scheduled for tomorrow at 10:00 AM in the main conference room.\n\nBest,\nHR Department",
        "attachments": [],
        "correct": "legit"
    },
    # Phishing
    {
        "subject": "Your account has been suspended",
        "sender": "support@paypa1.com",
        "body": "Dear Customer,\n\nWe noticed suspicious activity in your account. Please verify your information immediately by clicking the link below:\nhttp://paypa1-security.com/verify\n\nFailure to do so will result in permanent suspension.",
        "attachments": [],
        "correct": "phish"
    },
    {
        "subject": "Unusual sign-in activity",
        "sender": "security-alert@microsoft-support.com",
        "body": "We've detected unusual sign-in activity on your Microsoft account. Please confirm your identity by downloading the attached form and replying with your credentials.",
        "attachments": ["SecurityForm.docx"],
        "correct": "phish"
    },
    {
        "subject": "Congratulations! You've won a $500 gift card",
        "sender": "promo@amaz0n.com",
        "body": "Dear Winner,\n\nYou have been selected to receive a $500 Amazon gift card. Click the link below to claim your prize:\nhttp://amaz0n-prizes.com/claim\n\nAct fast, this offer expires soon!",
        "attachments": [],
        "correct": "phish"
    }
]

# --- AI-Like Email Generator ---
def generate_ai_email(difficulty):
    legit_subjects = [
        "Your invoice for last month",
        "Team meeting scheduled",
        "Welcome to our service",
        "Password changed successfully",
        "Your subscription is active"
    ]
    legit_senders = [
        "billing@company.com",
        "hr@company.com",
        "support@trustedsite.com",
        "no-reply@service.com",
        "admin@company.com"
    ]
    legit_bodies = [
        "Dear user, your invoice for last month is attached. Thank you for your business.",
        "The team meeting is scheduled for tomorrow at 10 AM in the main conference room.",
        "Thank you for signing up! Let us know if you have any questions.",
        "Your password was changed successfully. If this wasn't you, contact support.",
        "Your subscription is now active. Enjoy our premium features!"
    ]

    phish_subjects = [
        "URGENT: Account Suspended",
        "Verify your account now",
        "Unusual login detected",
        "Claim your reward",
        "Payment failed"
    ]
    phish_senders = [
        "security@secure-mail.com",
        "alert@bank-secure.com",
        "admin@paypall.com",
        "support@amaz0n.com",
        "it-support@company-secure.com"
    ]
    phish_bodies = [
        "Your account has been suspended. Click the link to reactivate.",
        "We noticed unusual activity. Please verify your account immediately.",
        "Congratulations! You have won a $1000 gift card. Click here to claim.",
        "Your payment could not be processed. Update your billing information.",
        "Immediate action required: Your account will be locked unless you respond."
    ]

    is_phish = random.random() < (0.5 + 0.1 * (difficulty - 1))
    if is_phish:
        idx = random.randint(0, len(phish_subjects) - 1)
        return {
            "subject": phish_subjects[idx],
            "sender": phish_senders[idx],
            "body": phish_bodies[idx],
            "attachments": [],
            "correct": "phish"
        }
    else:
        idx = random.randint(0, len(legit_subjects) - 1)
        return {
            "subject": legit_subjects[idx],
            "sender": legit_senders[idx],
            "body": legit_bodies[idx],
            "attachments": [],
            "correct": "legit"
        }

# --- Game Logic ---
def clear_screen():
    print("\n" * 100)

def print_email(email, number):
    print(f"\n--- Email #{number} ---")
    print(f"From: {email['sender']}")
    print(f"To: you@example.com")
    print(f"Subject: {email['subject']}")
    print(f"\n{email['body']}")
    if email['attachments']:
        print(f"\nAttachments: {', '.join(email['attachments'])}")
    else:
        print("\nAttachments: None")
    print("-" * 40)

def get_user_choice():
    print("\nIs this email (P)hish, (L)egit, or do you want to (R)eport it?")
    while True:
        choice = input("Your choice [P/L/R]: ").strip().lower()
        if choice in ['p', 'l', 'r']:
            return choice
        print("Invalid input. Please enter P, L, or R.")

def main():
    print("=== Cyber Sleuths: Phish Busters (CLI Edition) ===")
    print("Can you spot the phish? Type 'help' for instructions or press Enter to start.")
    cmd = input("> ").strip().lower()
    if cmd == "help":
        print("\nHow to Play:")
        print(" - You'll be shown a series of emails.")
        print(" - For each, type P for Phish, L for Legit, or R to Report.")
        print(" - Correct answers earn points and streaks can give you bonus time.")
        print(" - Difficulty increases as you progress!\n")
        input("Press Enter to start...")
    clear_screen()

    score = 0
    correct_answers = 0
    incorrect_answers = 0
    streak = 0
    stage = 1
    difficulty = 1
    max_stage = 3
    emails_reviewed = 0
    time_limit = 60
    time_left = time_limit
    start_time = time.time()

    all_samples = EMAIL_SAMPLES[:]
    random.shuffle(all_samples)

    def update_difficulty():
        nonlocal difficulty, stage, time_left
        if correct_answers > 0 and correct_answers % 10 == 0 and stage < max_stage:
            stage += 1
            difficulty = stage
            # Reduce time for next stage
            time_left += 0  # No bonus time, but you can adjust if you want
            print(f"\n🎉 Stage {stage}! Difficulty increased.\n")

    email_number = 1
    while time_left > 0:
        clear_screen()
        # 30%+ AI chance based on difficulty
        ai_chance = 0.3 + (difficulty - 1) * 0.2
        if random.random() < ai_chance:
            email = generate_ai_email(difficulty)
        else:
            if not all_samples:
                all_samples = EMAIL_SAMPLES[:]
                random.shuffle(all_samples)
            email = all_samples.pop()
        print_email(email, email_number)
        email_number += 1

        print(f"\nTime Left: {max(time_left,0)}s | Score: {score} | Streak: {streak} | Difficulty: {['Easy','Medium','Hard'][difficulty-1]}")

        # Get user input and measure time taken
        question_start = time.time()
        choice = get_user_choice()
        question_end = time.time()
        elapsed = int(question_end - question_start)
        time_left -= elapsed
        emails_reviewed += 1

        # Evaluate answer
        correct = email['correct']
        if choice == 'p':
            if correct == "phish":
                score += 10
                correct_answers += 1
                streak += 1
                print("✅ Correct! It's a phish.")
            else:
                score -= 5
                incorrect_answers += 1
                streak = 0
                print("❌ Incorrect. That was a legit email.")
        elif choice == 'l':
            if correct == "legit":
                score += 10
                correct_answers += 1
                streak += 1
                print("✅ Correct! It's legit.")
            else:
                score -= 5
                incorrect_answers += 1
                streak = 0
                print("❌ Incorrect. That was a phishing email.")
        elif choice == 'r':
            if correct == "phish":
                score += 5
                correct_answers += 1
                streak += 1
                print("📨 Reported! Good job.")
            else:
                score -= 2
                incorrect_answers += 1
                streak = 0
                print("⚠️ Not a phish. Incorrect report.")

        # Streak bonus
        if streak > 0 and streak % 3 == 0:
            time_left += 5
            print("⏱ +5s streak bonus!")

        update_difficulty()

        if time_left <= 0:
            break  # Just break, don't print GAME OVER here

        print("\n" + "="*50 + "\n")
        time.sleep(1)

    # Game Over
    clear_screen()
    print("⏰ Time's up!\n")
    print("=== GAME OVER ===")
    print(f"Final Score: {score}")
    print(f"Emails Reviewed: {emails_reviewed}")
    print(f"Correct: {correct_answers}")
    print(f"Incorrect: {incorrect_answers}\n")
    print("Thank you for playing Cyber Sleuths: Phish Busters!")
    print("© 2025 Kenji Plando. All rights reserved. GitHub: https://github.com/metaxenopy")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
        sys.exit(0)