const imageContainer = document.getElementById('image-container');
const loading = document.getElementById('loading');
const enumDropdown = document.getElementById('enum-dropdown');
const dataInfo = document.getElementById('data-info');
const lastUpdate = document.getElementById('last-update');
const nextBus = document.getElementById('next-bus');
const errorMessage = document.getElementById('error-message');
const flagsContainer = document.getElementById('flags-dropdown-custom');
const longTimeLoading = document.getElementById('long-time-loading');
const wifi_icon_size = "0.8em";
const wifi_icon_y = "10px";

const wifi_icon_html = `
<span class="wifi-icon" style="display:inline-block;vertical-align:${wifi_icon_y};width:${wifi_icon_size};height:${wifi_icon_size};margin-left:-5px;">
  <svg viewBox="0 0 17 18" width="100%" height="100%">
    <path class="arc3" d="M1 2 A14 14 0 0 1 15 16.5" fill="none" stroke="#ffffff" stroke-width="1.7" stroke-linecap="round"/>
    <path class="arc2" d="M1 7 A9 9 0 0 1 10 16.5" fill="none" stroke="#ffffff" stroke-width="1.7" stroke-linecap="round"/>
    <path class="arc1" d="M1 12 A4 4 0 0 1 5 16.5" fill="none" stroke="#ffffff" stroke-width="1.7" stroke-linecap="round"/>
  </svg>
</span>`;



let selectedFlags = 0;
let currentFetchController = null;

function setFavicon(imgSrc) {
    let link = document.querySelector("link[rel~='icon']");
    if (!link) {
        link = document.createElement('link');
        link.rel = 'icon';
        document.getElementsByTagName('head')[0].appendChild(link);
    }
    link.href = imgSrc;
}

function updateFlagsVisibility() {
    const selected = enumDropdown.value;
    const options = flagsContainer.getElementsByClassName("option");

    Array.from(options).forEach(div => {
        const related = div.getAttribute('related');
        div.style.display = related === selected ? 'flex' : 'none';
        if (related !== selected) div.classList.remove('selected');
    });
}

flagsContainer.addEventListener('click', (e) => {
    if (!e.target.classList.contains('option')) return;

    const flagValue = parseInt(e.target.dataset.value);

    if (e.target.classList.contains('selected')) {
        e.target.classList.remove('selected');
        selectedFlags &= ~flagValue;
    } else {
        e.target.classList.add('selected');
        selectedFlags |= flagValue;
    }

    localStorage.setItem('lastSelection', JSON.stringify({
        enumValue: enumDropdown.value,
        flags: selectedFlags
    }));

    fetchData();
});

const fetchData = () => {
    if (currentFetchController) currentFetchController.abort();
    currentFetchController = new AbortController();
    const signal = currentFetchController.signal;

    updateFlagsVisibility();
    setFavicon('images/logo.png');

    loading.style.display = 'block';
    longTimeLoading.style.display = 'none';
    dataInfo.style.display = 'none';
    imageContainer.innerHTML = '';
    imageContainer.appendChild(loading);
    errorMessage.textContent = '';

    const enumValue = parseInt(enumDropdown.value);
    const flags = selectedFlags;

    const test = window.location.hostname.includes("localhost");

    const url = test ?
        `http://localhost:5000/api/${enumValue}/${flags}` :
        `https://b1-or-21jet-backend.onrender.com/api/${enumValue}/${flags}`;

    let longLoadingTimer = setTimeout(() => {
        longTimeLoading.style.display = 'block';
    }, 10000);

    fetch(url, {
        method: "get",
        headers: new Headers({
            "ngrok-skip-browser-warning": "69420",
        }),
        signal
    })
        .then(response => {
            clearTimeout(longLoadingTimer);
            longTimeLoading.style.display = 'none';
            if (!response.ok) throw new Error('Erreur réseau');
            return response.json();
        })
        .then(data => {
            loading.style.display = 'none';
            if (data.status !== 'success') throw new Error('Erreur dans la réponse');

            dataInfo.style.display = 'flex';

            let bus_to_take = "none";

            if (data['21jet_prob'] === 0 && data['b1_prob'] === 0) {
                imageContainer.textContent = "Pas de bus disponible";
                setFavicon('images/logo.png');
            } else if (data['21jet_prob'] > data['b1_prob']) {
                const img = document.createElement('img');
                img.src = 'images/21jet_logo.svg';
                setFavicon('images/21jet_logo.svg');
                imageContainer.appendChild(img);

                bus_to_take = "21jet";
            } else {
                const img = document.createElement('img');
                img.src = 'images/b1_logo.svg';
                setFavicon('images/b1_logo.svg');
                imageContainer.appendChild(img);

                bus_to_take = "b1";
            }

            if ((data['next_bus_time'] !== undefined && data['next_bus_time'] !== -1))
            {
                nextBus.style.display = 'block';

                let minutes = Math.ceil(parseFloat(data['next_bus_time']) / 60);
                let bus_text = bus_to_take === "none" ? "bus" : bus_to_take === "b1" ? `<span style="color:rgba(229, 0, 107)">B1</span>` : `<span style="color:rgba(240, 127, 60)">21Jet</span>`;
                let msg_minutes = minutes == 0 ? "En vue" : minutes;

                nextBus.innerHTML = `Prochain ${bus_text} : <b>${msg_minutes}</b>` + wifi_icon_html;
            }

            const date = new Date(data.time * 1000);
            lastUpdate.innerHTML = `Dernière mise à jour : <b>${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}</b>`;
        })
        .catch(err => {
            clearTimeout(longLoadingTimer);
            longTimeLoading.style.display = 'none';
            loading.style.display = 'none';
            imageContainer.textContent = '';

            if (err.name === 'AbortError') return;
            errorMessage.textContent = `Erreur: ${err.message}`;
        });
};

window.addEventListener('load', () => {
    const saved = localStorage.getItem('lastSelection');
    if (saved) {
        const { enumValue, flags } = JSON.parse(saved);
        enumDropdown.value = enumValue;
        selectedFlags = flags;

        const options = flagsContainer.getElementsByClassName('option');
        Array.from(options).forEach(div => {
            const flagValue = parseInt(div.dataset.value);
            if ((flags & flagValue) !== 0) div.classList.add('selected');
            else div.classList.remove('selected');
        });
    }

    fetchData();
});

enumDropdown.addEventListener('change', () => {
    localStorage.setItem('lastSelection', JSON.stringify({
        enumValue: enumDropdown.value,
        flags: selectedFlags
    }));
    fetchData();
});
