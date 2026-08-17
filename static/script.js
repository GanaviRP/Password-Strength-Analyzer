let passwordInput =
    document.getElementById("password");


// ANALYZE PASSWORD 

async function analyzePassword() {

    const password = passwordInput.value;

    if (password.length === 0) {

        document.getElementById("strengthText")
            .textContent = "-";

        document.getElementById("strengthProgress")
            .style.width = "0%";

        resetChecks();

        return;
    }


    const response = await fetch("/analyze", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            password: password
        })

    });


    const result = await response.json();


    // Strength

    document.getElementById("strengthText")
        .textContent = result.strength;


    // Progress

    let percentage =
        (result.score / 8) * 100;

    document.getElementById(
        "strengthProgress"
    ).style.width = percentage + "%";


    // Strength color

    let progress =
        document.getElementById(
            "strengthProgress"
        );


    if (result.strength === "Weak") {

        progress.style.background = "#ef4444";

    } else if (result.strength === "Medium") {

        progress.style.background = "#f59e0b";

    } else if (result.strength === "Strong") {

        progress.style.background = "#22c55e";

    } else {

        progress.style.background = "#00ffaa";
    }


    // Checks

    result.checks.forEach(
        (check, index) => {

            const element =
                document.getElementById(
                    "check" + index
                );

            if (check.passed) {

                element.classList.add("passed");

                element.textContent =
                    "✓ " + check.name;

            } else {

                element.classList.remove("passed");

                element.textContent =
                    "❌ " + check.name;
            }

        }
    );


    // Suggestions

    const list =
        document.getElementById(
            "suggestionsList"
        );

    list.innerHTML = "";


    result.suggestions.forEach(
        suggestion => {

            const li =
                document.createElement("li");

            li.textContent = suggestion;

            list.appendChild(li);
        }
    );
}


//  RESET CHECKS 

function resetChecks() {

    const checks = document.querySelectorAll(
        ".checks div"
    );

    checks.forEach(
        (element, index) => {

            element.classList.remove("passed");

            const names = [
                "At least 12 characters",
                "Uppercase letter",
                "Lowercase letter",
                "Number",
                "Special character",
                "Not a common password",
                "No repeated characters"
            ];

            element.textContent =
                "❌ " + names[index];
        }
    );
}


//  SHOW / HIDE 

function togglePassword() {

    const input =
        document.getElementById("password");

    const button =
        document.getElementById("eyeButton");


    if (input.type === "password") {

        input.type = "text";

        button.textContent = "🙈";

    } else {

        input.type = "password";

        button.textContent = "👁";
    }
}


//  GENERATE PASSWORD

async function generatePassword() {

    const response =
        await fetch("/generate");

    const result =
        await response.json();


    document.getElementById(
        "generatedPassword"
    ).value = result.password;
}


//  COPY PASSWORD 

function copyPassword() {

    const password =
        document.getElementById(
            "generatedPassword"
        ).value;


    if (!password) {

        return;
    }


    navigator.clipboard.writeText(password);


    document.getElementById(
        "copyMessage"
    ).textContent =
        "✓ Password copied!";
}