async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a file");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("result").classList.add("hidden");

    try {
        const response = await fetch("http://127.0.0.1:8000/analyze", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        document.getElementById("loading").classList.add("hidden");
        document.getElementById("result").classList.remove("hidden");

        document.getElementById("verdict").innerText = data.verdict;
        document.getElementById("trust").innerText = data.trust_score;
        document.getElementById("prob").innerText = data.fake_probability;

        const reasonsList = document.getElementById("reasons");
        reasonsList.innerHTML = "";

        data.reasons.forEach(reason => {
            const li = document.createElement("li");
            li.innerText = reason;
            reasonsList.appendChild(li);
        });

        document.getElementById("ai").innerText = data.ai_explanation || "No AI explanation";

    } catch (error) {
        alert("Error connecting to backend");
        console.error(error);
    }
}