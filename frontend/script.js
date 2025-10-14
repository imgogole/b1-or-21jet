const imageContainer = document.getElementById('image-container');
const loading = document.getElementById('loading');
const enumDropdown = document.getElementById('enum-dropdown');
const lastUpdate = document.getElementById('last-update');
const errorMessage = document.getElementById('error-message');
const flagsContainer = document.getElementById('flags-dropdown-custom');
const longTimeLoading = document.getElementById('long-time-loading');

let selectedFlags = 0;

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
    updateFlagsVisibility();
    setFavicon('images/logo.png');

    loading.style.display = 'block';
    longTimeLoading.style.display = 'none';
    imageContainer.innerHTML = '';
    imageContainer.appendChild(loading);
    errorMessage.textContent = '';

    const enumValue = parseInt(enumDropdown.value);
    const flags = selectedFlags;

    const url = window.location.hostname.includes("localhost") ? `http://localhost:5000/api/${enumValue}/${flags}` : `https://b1-or-21jet-backend.onrender.com/api/${enumValue}/${flags}`;

    let longLoadingTimer = setTimeout(() => {
        longTimeLoading.style.display = 'block';
    }, 10000);

    fetch(url, {
        method: "get",
        headers: new Headers({
            "ngrok-skip-browser-warning": "69420",
        }),
    })
        .then(response => {
            clearTimeout(longLoadingTimer);
            longTimeLoading.style.display = 'none';
            console.log(response);
            if (!response.ok) throw new Error('Erreur réseau');
            return response.json();
        })
        .then(data => {

            loading.style.display = 'none';
            if (data.status !== 'success') {
                throw new Error('Erreur dans la réponse');
            }
            if (data['21jet_prob'] === 0 && data['b1_prob'] === 0) {
                imageContainer.textContent = "Pas de bus disponible";
                setFavicon('images/logo.png');
            } else if (data['21jet_prob'] > data['b1_prob']) {
                const img = document.createElement('img');
                img.src = 'images/21jet_logo.svg';
                setFavicon('images/21jet_logo.svg');
                imageContainer.appendChild(img);
            } else {
                const img = document.createElement('img');
                img.src = 'images/b1_logo.svg';
                setFavicon('images/b1_logo.svg');
                imageContainer.appendChild(img);
            }

            const date = new Date(data.time * 1000);
            lastUpdate.innerHTML = `Dernière mise à jour : <b>${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}</b>`;
        })
        .catch(err => {
            clearTimeout(longLoadingTimer);
            longTimeLoading.style.display = 'none';
            loading.style.display = 'none';
            imageContainer.textContent = '';
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
            if ((flags & flagValue) !== 0) {
                div.classList.add('selected');
            } else {
                div.classList.remove('selected');
            }
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