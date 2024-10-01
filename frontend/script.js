const uploadButton = document.getElementById('upload-button');
const fileInput = document.getElementById('file-input');
const loading = document.getElementById('loading');
const dynamicInputs = document.getElementById('dynamic-inputs');
const processButton = document.getElementById('process-button');
const resultImage = document.getElementById('result-image');
const downloadButton = document.getElementById('download-button');
const detailsButton = document.getElementById('details-button');

let targetId = '';
let inputsData = {};

async function fetchWithRetry(url, options = {}, retries = 3, delay = 1000) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url, options);
            if (response.status === 200) {
                return response; // If status is 200, return the response.
            } else {
                console.log(`Attempt ${i + 1} failed with status: ${response.status}`);
            }
        } catch (error) {
            console.log(`Attempt ${i + 1} failed with error: ${error.message}`);
        }

        if (i < retries - 1) {
            // If it's not the last attempt, wait for the specified delay.
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
    throw new Error(`Failed to fetch after ${retries} retries.`);
}

// Upload Button Click
uploadButton.addEventListener('click', () => {
    fileInput.click();
});

// File Input Change
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
        uploadFile(file);
    }
});

// Upload File Function
function uploadFile(file) {
    uploadButton.style.display = 'none';
    loading.style.display = 'block';

    const formData = new FormData();
    formData.append('file', file);

    fetchWithRetry('/rest/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        loading.style.display = 'none';
        targetId = data.target_id;
        inputsData = data.inputs;

        if (Object.keys(inputsData).length === 0) {
            // No inputs, proceed to processing
            processInputs({});
        } else {
            // Generate Inputs
            generateInputs(inputsData);
            processButton.style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        loading.style.display = 'none';
        uploadButton.style.display = 'block';
    });
}


// Generate Inputs Function
function generateInputs(inputs) {
    dynamicInputs.innerHTML = '';
    for (const [id, input] of Object.entries(inputs)) {
        const div = document.createElement('div');
        div.className = 'input-field';

        if (input.type === 'toggle') {
            const label = document.createElement('label');
            label.innerText = id + ': ';
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = input.value || false;
            checkbox.id = id;
            label.appendChild(checkbox);
            div.appendChild(label);
        } else if (input.type === 'dropdown') {
            const label = document.createElement('label');
            label.innerText = id + ': ';
            const select = document.createElement('select');
            select.id = id;
            input.items.forEach(item => {
                const option = document.createElement('option');
                option.value = item;
                option.text = item;
                select.appendChild(option);
            });
            div.appendChild(label);
            div.appendChild(select);
        } else if (input.type === 'checkbox') {
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = id;
            checkbox.dataset.group = input.group || '';
            const label = document.createElement('label');
            label.className = 'inline-label';
            label.htmlFor = id;
            label.innerText = id;
            div.appendChild(checkbox);
            div.appendChild(label);
        } else if (input.type === 'radio') {
            const radio = document.createElement('input');
            radio.type = 'radio';
            radio.id = id;
            radio.name = input.group || id;
            const label = document.createElement('label');
            label.className = 'inline-label';
            label.htmlFor = id;
            label.innerText = id;
            div.appendChild(radio);
            div.appendChild(label);
        } else if (input.type === 'text') {
            const label = document.createElement('label');
            label.innerText = id + ': ';
            const textInput = document.createElement('input');
            textInput.type = 'text';
            textInput.id = id;
            textInput.value = input.default || '';
            div.appendChild(label);
            div.appendChild(textInput);
        }

        dynamicInputs.appendChild(div);
    }
}

// Process Button Click
processButton.addEventListener('click', () => {
    const inputsValues = {};
    for (const [id, input] of Object.entries(inputsData)) {
        const element = document.getElementById(id);
        if (input.type === 'toggle' || input.type === 'checkbox') {
            inputsValues[id] = element.checked;
        } else if (input.type === 'dropdown') {
            inputsValues[id] = element.value;
        } else if (input.type === 'radio') {
            inputsValues[id] = element.checked;
        } else if (input.type === 'text') {
            inputsValues[id] = element.value;
        }
    }
    processInputs(inputsValues);
});
let image_url_const;
// Process Inputs Function
function processInputs(inputsValues) {
    dynamicInputs.style.display = 'none';
    processButton.style.display = 'none';
    loading.style.display = 'block';

    const payload = {
        inputs: inputsValues,
        target_id: targetId
    };

    fetchWithRetry('/rest/process/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error){
            alert(data.error);
            location.reload();
            return;
        }
        loading.style.display = 'none';
        image_url_const = data.image_url;
        displayResult(data.image_url);
    })
    .catch(error => {
        console.error('Error:', error);
        loading.style.display = 'none';
    });
}

// Display Result Function
function displayResult(imageUrl) {
    resultImage.src = imageUrl;
    
    resultImage.style.display = 'block';
    downloadButton.style.display = 'block';
    detailsButton.style.display = 'block';
}

detailsButton.addEventListener('click', function() {
    // Send POST request before opening the new page
    const id = image_url_const.match(/\/.*\/([a-z0-9]+)\..*/)[1]
    const newWindow = window.open('details.html?result='+id, '_blank');
});

downloadButton.addEventListener('click', () => {
    const link = document.createElement('a');
    link.href = resultImage.src;
    link.download = 'wordcloud.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});


const helpButton = document.getElementById('help-button');

helpButton.addEventListener('click', () => {
    // Create help window
    const helpWindow = document.createElement('div');
    helpWindow.id = 'help-window';
    helpWindow.className = 'help-window';
    document.body.appendChild(helpWindow);
    
    // Add close button
    const closeButton = document.createElement('button');
    closeButton.id = 'close-help-button';
    closeButton.innerText = 'Close';
    closeButton.className = 'close-help-button';
    helpWindow.appendChild(closeButton);
    
    // Add content area
    const helpContent = document.createElement('div');
    helpContent.id = 'help-content';
    helpContent.className = 'help-content';
    helpWindow.appendChild(helpContent);
    
    fetch('/help.txt')
        .then(response => response.text())
        .then(text => {
            helpContent.innerText = text;
        })
        .catch(error => {
            helpContent.innerText = 'Failed to load help content.';
            console.error('Error loading help content:', error);
        });
    
    // Close button event
    closeButton.addEventListener('click', () => {
        document.body.removeChild(helpWindow);
    });
});