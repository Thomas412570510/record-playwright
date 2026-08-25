const fs = require('fs');
const path = require('path');
const ffmpeg = require('fluent-ffmpeg');
const ffmpegStatic = require('ffmpeg-static');

ffmpeg.setFfmpegPath(ffmpegStatic);

const rootDir = path.join(__dirname, '../../../../../');
const testResultsDir = path.join(rootDir, 'test-results');
const testsDir = path.join(rootDir, 'tests');

if (!fs.existsSync(testResultsDir)) {
  console.log('找不到 test-results 資料夾。');
  process.exit(0);
}

const specFiles = fs.existsSync(testsDir) 
  ? fs.readdirSync(testsDir).filter(f => f.endsWith('.spec.ts')).map(f => f.replace('.spec.ts', ''))
  : [];

function findWebmFiles(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    const filePath = path.join(dir, file);
    if (fs.statSync(filePath).isDirectory()) {
      results = results.concat(findWebmFiles(filePath));
    } else if (filePath.endsWith('.webm')) {
      results.push(filePath);
    }
  });
  return results;
}

const webmFiles = findWebmFiles(testResultsDir);

if (webmFiles.length === 0) {
  console.log('沒有找到任何 .webm 影片檔案');
  process.exit(0);
}

console.log(`找到 ${webmFiles.length} 部影片，準備進行智慧分類與轉檔...`);

function convertFile(webmPath) {
  return new Promise((resolve, reject) => {
    const folderName = path.basename(path.dirname(webmPath));
    let scriptName = 'Uncategorized';
    let testName = folderName;
    
    for (const spec of specFiles) {
      if (folderName.startsWith(spec + '-')) {
        scriptName = spec;
        testName = folderName.replace(spec + '-', '').replace(/-retry\d+$/, '');
        break;
      }
    }

    const outDir = path.join(testResultsDir, scriptName);
    if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
    
    const mp4Path = path.join(outDir, `${testName}.mp4`);
    const sourceDir = path.dirname(webmPath);

    // 🌟 智慧搬運：將同目錄下的報錯報告、截圖、軌跡檔一起搬運過去！
    try {
      fs.readdirSync(sourceDir).forEach(file => {
        const ext = path.extname(file);
        if (['.md', '.png', '.zip'].includes(ext)) {
          const srcFile = path.join(sourceDir, file);
          const destFile = path.join(outDir, `${testName}-${file}`);
          if (!fs.existsSync(destFile)) {
            fs.copyFileSync(srcFile, destFile);
          }
        }
      });
    } catch (e) {
      console.log(`[附屬檔案搬運失敗] ${e.message}`);
    }
    
    if (fs.existsSync(mp4Path)) {
      console.log(`[跳過影片] 已存在 ${mp4Path}`);
      return resolve();
    }

    console.log(`[分類轉檔中] ${scriptName} / ${testName} -> .mp4`);
    
    ffmpeg(webmPath)
      .output(mp4Path)
      .on('end', () => resolve())
      .on('error', (err) => reject(err))
      .run();
  });
}

async function run() {
  for (const file of webmFiles) {
    try { await convertFile(file); } catch (e) { }
  }
  console.log('🎉 影片已全部分類並轉檔完成！請至 test-results/ 內查看專屬腳本資料夾。');
}

run();
