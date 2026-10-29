from flask import Flask, render_template, request

from db import generate_users

app = Flask(__name__)

LOCALES = {
    "en_US": "English (United States)",
    "de_DE": "German (Germany)",
}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    users = []
    locale = "en_US"
    seed = "demo-seed"
    batch_index = 0
    batch_size = 10

    if request.method == "POST":
        locale = request.form.get("locale", "en_US")
        seed = request.form.get("seed", "demo-seed").strip()
        try:
            batch_index = int(request.form.get("batch_index", "0"))
            batch_size = int(request.form.get("batch_size", "10"))
            if locale not in LOCALES:
                raise ValueError("Choose a supported locale.")
            if not seed or len(seed) > 200:
                raise ValueError("Seed must contain 1–200 characters.")
            if batch_index < 0:
                raise ValueError("Batch index cannot be negative.")
            if not 1 <= batch_size <= 100:
                raise ValueError("Batch size must be between 1 and 100.")
            users = generate_users(locale, seed, batch_index, batch_size)
        except ValueError as exc:
            error = str(exc)
        except Exception:
            error = (
                "Could not generate users. Check the database connection "
                "and try again."
            )

    return render_template(
        "index.html",
        error=error,
        users=users,
        locales=LOCALES,
        locale=locale,
        seed=seed,
        batch_index=batch_index,
        batch_size=batch_size,
    )


if __name__ == "__main__":
    app.run(debug=True)
