const goodId = document.getElementById("goodId")
const badId = document.getElementById("badId")

const goodValue = document.getElementById("goodValue")
const badValue = document.getElementById("badValue")

const goodNames = document.getElementById("goodnames")
const badNames = document.getElementById("badnames")

async function fetchText() {
    let response = await fetch('/good');
    let data = await response.json();
    goodId.textContent= data["Good dev"]
    badId.textContent = data["Bad dev"]

    goodValue.textContent = data["Current val good"]
    badValue.textContent = data["Current val bad"]

    goodNames.textContent = data["Good names"]
    badNames.textContent = data["Bad names"]


    


}

setInterval(fetchText,60000)
