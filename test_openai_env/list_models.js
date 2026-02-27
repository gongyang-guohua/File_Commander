
const apiKey = "AIzaSyCW7aJCBWLKQkGfBnC8nhC2jC1UWFXPilY"; // Masked

async function main() {
    console.log("Listing available models from Google API...");
    // Standard Gemini API endpoint for listing models
    const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`;

    try {
        const response = await fetch(url);
        if (!response.ok) {
            console.log(`Fetch Status: ${response.status} ${response.statusText}`);
            const text = await response.text();
            console.log(`Body: ${text}`);
        } else {
            const data = await response.json();
            console.log("Models found:");
            if (data.models) {
                data.models.forEach(m => {
                    console.log(`- ${m.name} (DisplayName: ${m.displayName})`);
                    // Check if it supports generateContent
                    if (m.supportedGenerationMethods) {
                        console.log(`  Methods: ${m.supportedGenerationMethods.join(", ")}`);
                    }
                });
            } else {
                console.log("No models returned.");
            }
        }
    } catch (e) {
        console.log("Fetch Error: " + e.message);
    }
}

main();
