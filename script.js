async function getWeather() {

    const summary =
        document.getElementById("summary");

    const hourlyDiv =
        document.getElementById("hourly");

    const errorDiv =
        document.getElementById("error");


    try {

        errorDiv.innerText = "";

        summary.innerText =
            "Loading weather...";

        hourlyDiv.innerHTML =
            "<p>Loading hourly weather...</p>";


        const response =
            await fetch("/weather");


        if (!response.ok) {

            throw new Error(
                "Weather request failed"
            );

        }


        const data =
            await response.json();


        // =========================
        // TODAY
        // =========================

        const today =
            data.today;


        document.getElementById(
            "rainProbability"
        ).innerText =
            today.rain_probability + "%";


        document.getElementById(
            "rainMm"
        ).innerText =
            today.rain_mm + " mm";


        document.getElementById(
            "maxTemp"
        ).innerText =
            today.max_temperature + " °C";


        document.getElementById(
            "minTemp"
        ).innerText =
            today.min_temperature + " °C";


        // =========================
        // AI SUMMARY
        // =========================

        summary.innerText =
            data.summary;


        // =========================
        // HOURLY WEATHER
        // =========================

        hourlyDiv.innerHTML = "";


        data.hourly.forEach(hour => {

            const div =
                document.createElement("div");


            div.className = "hour";


            div.innerHTML = `

                <strong>
                    ${formatTime(hour.time)}
                </strong>

                <span>
                    🌡️ ${hour.temperature}°C
                </span>

                <span>
                    🌧️ ${hour.rain_probability}%
                </span>

                <span>
                    💧 ${hour.humidity}%
                </span>

                <span>
                    💨 ${hour.wind_speed} km/h
                </span>

                <span>
                    🌧️ ${hour.rain_mm} mm
                </span>

            `;


            hourlyDiv.appendChild(div);

        });


    }

    catch (error) {

        console.error(error);


        errorDiv.innerText =
            "Unable to fetch weather. Please try again.";


        summary.innerText = "";


        hourlyDiv.innerHTML = "";

    }

}


// =========================
// TIME FORMAT
// =========================

function formatTime(timeString) {

    const date =
        new Date(timeString);


    return date.toLocaleTimeString([], {

        hour: "2-digit",

        minute: "2-digit"

    });

}


// =========================
// TEXT TO SPEECH
// =========================

function speakSummary() {

    const text =
        document.getElementById("summary").innerText;


    if (!text) {
        return;
    }


    const speech =
        new SpeechSynthesisUtterance(text);


    speech.lang = "te-IN";


    window.speechSynthesis.speak(
        speech
    );

}