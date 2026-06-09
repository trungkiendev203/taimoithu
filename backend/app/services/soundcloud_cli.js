const scdl = require('E:/fashion-ecommerce/node-soundcloud-downloader').default;
const fs = require('fs');

async function main() {
    const action = process.argv[2];
    const url = process.argv[3];
    
    if (!action || !url) {
        console.error(JSON.stringify({error: "Missing arguments"}));
        process.exit(1);
    }
    
    try {
        if (!scdl.isValidUrl(url)) {
            console.error(JSON.stringify({error: "Invalid SoundCloud URL"}));
            process.exit(1);
        }

        if (action === "info") {
            const info = await scdl.getInfo(url);
            console.log(JSON.stringify({
                title: info.title,
                duration: info.duration,
                uploader: info.user ? info.user.username : "Unknown",
                thumbnail: info.artwork_url ? info.artwork_url.replace('-large', '-t500x500') : (info.user ? info.user.avatar_url : null)
            }));
            process.exit(0);
        } else if (action === "download") {
            const outputPath = process.argv[4];
            if (!outputPath) {
                console.error(JSON.stringify({error: "Missing output path"}));
                process.exit(1);
            }
            const stream = await scdl.download(url);
            const writeStream = fs.createWriteStream(outputPath);
            stream.pipe(writeStream);
            
            writeStream.on('finish', () => {
                console.log(JSON.stringify({success: true}));
                process.exit(0);
            });
            writeStream.on('error', (err) => {
                console.error(JSON.stringify({error: err.message}));
                process.exit(1);
            });
            stream.on('error', (err) => {
                console.error(JSON.stringify({error: err.message}));
                process.exit(1);
            });
        }
    } catch (e) {
        console.error(JSON.stringify({error: e.message}));
        process.exit(1);
    }
}

main();
