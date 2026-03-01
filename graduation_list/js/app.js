// グローバル変数
let currentData = null;
let currentFileName = '';
let currentGrade = 'PGY1';

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    initializeUploadScreen();
    setupEventListeners();
});

// アップロード画面の初期化
function initializeUploadScreen() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    
    // ドラッグ&ドロップイベント
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('border-blue-500', 'bg-blue-50');
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-blue-500', 'bg-blue-50');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('border-blue-500', 'bg-blue-50');
        const file = e.dataTransfer.files[0];
        if (file) handleFileUpload(file);
    });
    
    // ファイル選択イベント
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) handleFileUpload(file);
    });
}

// イベントリスナーの設定
function setupEventListeners() {
    document.getElementById('changeFileBtn').addEventListener('click', () => {
        document.getElementById('mainScreen').classList.add('hidden');
        document.getElementById('uploadScreen').classList.remove('hidden');
        document.getElementById('fileInput').value = '';
        document.getElementById('errorMessage').classList.add('hidden');
    });
}

// ファイルアップロード処理
async function handleFileUpload(file) {
    // エラーメッセージをクリア
    hideError();
    
    // ファイル形式チェック
    if (!file.name.endsWith('.xlsx')) {
        showError('.xlsxファイルを選択してください');
        return;
    }
    
    currentFileName = file.name;
    showLoading(true);
    
    try {
        // ファイルを読み込む
        const arrayBuffer = await file.arrayBuffer();
        const workbook = XLSX.read(arrayBuffer, { type: 'array' });
        
        // Sheet1の存在チェック（他のシートがあっても問題なし）
        if (!workbook.SheetNames || workbook.SheetNames.length === 0) {
            showError('シートが見つかりません。ファイルを確認してください');
            showLoading(false);
            return;
        }
        
        // Sheet1が存在しない場合のエラーハンドリング
        if (!workbook.SheetNames.includes('Sheet1')) {
            showError('Sheet1が見つかりません。ファイルを確認してください');
            showLoading(false);
            return;
        }
        
        // Sheet1を取得（他のシートがあっても問題なく動作）
        const worksheet = workbook.Sheets['Sheet1'];
        // ヘッダー行をスキップして2行目以降を読み込み
        const rawData = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: null });
        
        // データ解析
        const parsedData = parseExcelData(rawData);
        
        if (Object.keys(parsedData).length === 0) {
            showError('該当データが見つかりません');
            showLoading(false);
            return;
        }
        
        currentData = parsedData;
        
        // メイン画面を表示
        showLoading(false);
        displayMainScreen();
        
    } catch (error) {
        showError('ファイルの解析中にエラーが発生しました: ' + error.message);
        showLoading(false);
    }
}

// Excelデータの解析（要件定義書に基づく）
function parseExcelData(rawData) {
    const data = {};
    
    // ヘッダー行から列の位置を自動検出
    let gradeColumnIndex = null;
    let nameColumnIndex = null;
    
    if (rawData.length > 0 && rawData[0]) {
        const headerRow = rawData[0];
        for (let idx = 0; idx < headerRow.length; idx++) {
            const header = headerRow[idx] ? String(headerRow[idx]).trim() : '';
            if (header === '学年' && gradeColumnIndex === null) {
                gradeColumnIndex = idx;
            }
            if (header === '名前' && nameColumnIndex === null) {
                nameColumnIndex = idx;
            }
        }
    }
    
    // ヘッダーが見つからない場合のフォールバック（デフォルト位置）
    if (gradeColumnIndex === null) {
        // 最初の列がnullの場合は1つずらす
        if (rawData.length > 1 && rawData[1] && rawData[1][0] === null) {
            gradeColumnIndex = 1;
            nameColumnIndex = 4;
        } else {
            gradeColumnIndex = 0;
            nameColumnIndex = 3;
        }
    }
    if (nameColumnIndex === null) {
        nameColumnIndex = gradeColumnIndex + 3; // 学年から3列後ろ
    }
    
    
    // 列のオフセットを計算（学年列からの相対位置）
    const offset = gradeColumnIndex;
    
    // ヘッダー行をスキップして2行目以降を処理
    for (let i = 1; i < rawData.length; i++) {
        const row = rawData[i];
        
        // 列のマッピング（検出された列位置を使用）
        const grade = row[gradeColumnIndex] ? String(row[gradeColumnIndex]).trim() : null;
        const name = row[nameColumnIndex] ? String(row[nameColumnIndex]).trim() : null;
        
        // 学年と名前が両方存在する場合のみ有効データ（必須項目チェック）
        if (!grade || !name) {
            continue;
        }
        
        // PGYパターンのチェック（PGY1, PGY2, PGY3, PGY4, PGY5のみ有効）
        const pgyPattern = /PGY\d/i;
        if (!pgyPattern.test(grade)) {
            continue; // PGYパターンに一致しない場合はスキップ
        }
        
        // データオブジェクトを作成（検出された列位置からの相対位置を使用）
        const trainee = {
            name: name,
            furigana: row[offset + 4] ? String(row[offset + 4]).trim() : '', // 学年から4列後ろ: ふりがな
            gender: row[offset + 5] ? String(row[offset + 5]).trim() : '', // 学年から5列後ろ: 性別
            department: row[offset + 6] ? String(row[offset + 6]).trim() : '', // 学年から6列後ろ: 専門科
            course: row[offset + 7] ? String(row[offset + 7]).trim() : '', // 学年から7列後ろ: 進路
            survey: row[offset + 8] ? String(row[offset + 8]).trim() : '', // 学年から8列後ろ: 動向調査
            origin: row[offset + 9] ? String(row[offset + 9]).trim() : '', // 学年から9列後ろ: 本籍
            university: row[offset + 10] ? String(row[offset + 10]).trim() : '', // 学年から10列後ろ: 出身大学
            remarks: row[offset + 11] ? String(row[offset + 11]).trim() : '' // 学年から11列後ろ: 備考
        };
        
        // 学年別に初期化
        if (!data[grade]) {
            data[grade] = [];
        }
        
        data[grade].push(trainee);
    }
    
    return data;
}

// データの分類と重複排除（要件定義書に基づく）
function classifyData(gradeData) {
    const promoted = [];
    const transferred = [];
    const excluded = [];
    const reference = [];
    const seen = new Set();
    
    // 名前の正規化関数（スペース・全角スペース除去）
    const normalizeName = (name) => {
        return name.replace(/[\s　]/g, '');
    };
    
    for (const trainee of gradeData) {
        const normalizedName = normalizeName(trainee.name);
        
        // 重複チェック（同一学年内で名前を正規化して重複を排除）
        if (seen.has(normalizedName)) {
            continue; // 重複はスキップ
        }
        seen.add(normalizedName);
        
        // 参照リストには全て追加
        reference.push(trainee);
        
        const course = trainee.course || '';
        const remarks = trainee.remarks || '';
        
        // 除外対象チェック（要件定義書に基づく）
        // 進路列に「中断」「退職」「病休」が含まれる、または進路列が空の場合
        if (course.includes('中断') || course.includes('退職') || course.includes('病休') ||
            remarks.includes('中断') || remarks.includes('退職') || remarks.includes('病休') ||
            !course || course.trim() === '') {
            excluded.push(trainee);
            continue;
        }
        
        // 進級者（進路列に「進級」が含まれる）
        if (course.includes('進級')) {
            promoted.push(trainee);
        }
        // 転出・修了者（進路列に「転出」または「修了」が含まれる、または「転」のみ）
        else if (course.includes('転出') || course === '転' || course.includes('修了')) {
            transferred.push(trainee);
        }
        // その他は除外
        else {
            excluded.push(trainee);
        }
    }
    
    // 専門科でソート（進級者・転出者は専門科で昇順ソート）
    const sortByDepartment = (a, b) => {
        return (a.department || '').localeCompare(b.department || '', 'ja');
    };
    
    promoted.sort(sortByDepartment);
    transferred.sort(sortByDepartment);
    
    return { promoted, transferred, excluded, reference };
}

// 参照リストの行の背景色を取得（要件定義書に基づく色分けルール）
function getReferenceRowColor(trainee) {
    const course = trainee.course || '';
    const survey = trainee.survey || '';
    const remarks = trainee.remarks || '';
    
    // 進級: 白背景
    if (course.includes('進級')) return 'bg-white';
    
    // 転出: オレンジ薄
    if (course.includes('転出') || course === '転') return 'bg-orange-50';
    
    // 退職: 赤薄
    if (course.includes('退職') || remarks.includes('退職')) return 'bg-red-100';
    
    // 中断: 赤薄
    if (course.includes('中断') || remarks.includes('中断')) return 'bg-red-100';
    
    // 修了: 紫薄
    if (course.includes('修了')) return 'bg-purple-50';
    
    // 休職: グレー（進路が空で動向調査に「休職」が含まれる場合）
    if (!course && survey.includes('休職')) return 'bg-gray-200';
    
    // 進路未入力: 黄色薄（進路が空の場合）
    if (!course) return 'bg-yellow-50';
    
    return 'bg-white';
}

// 全体集計を計算
function calculateTotalStats() {
    let totalPromoted = 0;
    let totalTransferred = 0;
    
    Object.keys(currentData).forEach(grade => {
        const gradeData = currentData[grade];
        const { promoted, transferred } = classifyData(gradeData);
        totalPromoted += promoted.length;
        totalTransferred += transferred.length;
    });
    
    return { totalPromoted, totalTransferred };
}

// 全体集計を表示
function displayTotalStats() {
    const { totalPromoted, totalTransferred } = calculateTotalStats();
    document.getElementById('totalPromoted').textContent = totalPromoted;
    document.getElementById('totalTransferred').textContent = totalTransferred;
}

// メイン画面を表示
function displayMainScreen() {
    document.getElementById('fileName').textContent = `ファイル: ${currentFileName}`;
    document.getElementById('uploadScreen').classList.add('hidden');
    document.getElementById('mainScreen').classList.remove('hidden');
    
    // 全体集計を表示
    displayTotalStats();
    
    // タブを生成
    generateGradeTabs();
    
    // デフォルトで最初の学年を表示（PGY順にソート）
    const grades = Object.keys(currentData).sort((a, b) => {
        const pgyPattern = /PGY(\d+)/i;
        const matchA = a.match(pgyPattern);
        const matchB = b.match(pgyPattern);
        
        if (matchA && matchB) {
            return parseInt(matchA[1]) - parseInt(matchB[1]);
        }
        if (matchA) return -1;
        if (matchB) return 1;
        return a.localeCompare(b, 'ja');
    });
    
    if (grades.length > 0) {
        currentGrade = grades[0];
        displayGradeData(grades[0]);
    }
}

// 学年タブを生成
function generateGradeTabs() {
    const tabsContainer = document.getElementById('gradeTabs');
    tabsContainer.innerHTML = '';
    
    // PGY順にソート（PGY1, PGY2, PGY3, PGY4, PGY5の順）
    const grades = Object.keys(currentData).sort((a, b) => {
        const pgyPattern = /PGY(\d+)/i;
        const matchA = a.match(pgyPattern);
        const matchB = b.match(pgyPattern);
        
        if (matchA && matchB) {
            return parseInt(matchA[1]) - parseInt(matchB[1]);
        }
        if (matchA) return -1;
        if (matchB) return 1;
        return a.localeCompare(b, 'ja');
    });
    
    grades.forEach(grade => {
        const gradeData = currentData[grade];
        const { promoted, transferred } = classifyData(gradeData);
        
        const tab = document.createElement('button');
        tab.className = 'px-6 py-3 font-medium text-gray-700 hover:text-blue-600 border-b-2 border-transparent whitespace-nowrap';
        tab.dataset.grade = grade;
        tab.innerHTML = `
            ${grade}
            <span class="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">${promoted.length}名</span>
            <span class="ml-1 px-2 py-1 text-xs bg-orange-100 text-orange-800 rounded-full">${transferred.length}名</span>
        `;
        
        tab.addEventListener('click', () => {
            // 全タブの選択を解除
            document.querySelectorAll('#gradeTabs button').forEach(btn => {
                btn.classList.remove('text-blue-600', 'border-blue-600');
                btn.classList.add('text-gray-700', 'border-transparent');
            });
            
            // 選択したタブをアクティブに
            tab.classList.remove('text-gray-700', 'border-transparent');
            tab.classList.add('text-blue-600', 'border-blue-600');
            
            currentGrade = grade;
            displayGradeData(grade);
        });
        
        tabsContainer.appendChild(tab);
    });
    
    // 最初のタブをアクティブに
    if (grades.length > 0) {
        tabsContainer.firstChild.classList.remove('text-gray-700', 'border-transparent');
        tabsContainer.firstChild.classList.add('text-blue-600', 'border-blue-600');
    }
}

// 学年データを表示
function displayGradeData(grade) {
    const gradeData = currentData[grade];
    const { promoted, transferred, excluded, reference } = classifyData(gradeData);
    
    const mainContent = document.getElementById('mainContent');
    mainContent.innerHTML = `
        <!-- 3カラムレイアウト -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <!-- 左カラム: 進級者 -->
            <div class="bg-white rounded-lg shadow-md overflow-hidden">
                <div class="bg-blue-100 px-4 py-3">
                    <div class="flex justify-between items-center">
                        <h2 class="text-lg font-bold text-gray-800">進級者</h2>
                        <span class="text-xl font-bold text-blue-600">${promoted.length}名</span>
                    </div>
                </div>
                <div class="p-4">
                    <input type="text" id="promotedSearch" placeholder="名前で検索..." 
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg mb-3 focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <div class="overflow-auto custom-scrollbar" style="max-height: 65vh;">
                        <table class="w-full text-sm">
                            <thead class="bg-gray-50 sticky top-0">
                                <tr>
                                    <th class="px-2 py-2 text-left">No.</th>
                                    <th class="px-2 py-2 text-left">名前</th>
                                    <th class="px-2 py-2 text-left">専門科</th>
                                    <th class="px-2 py-2 text-left">出身大学</th>
                                </tr>
                            </thead>
                            <tbody id="promotedTable">
                                ${generatePromotedRows(promoted)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- 中央カラム: 転出・修了者 -->
            <div class="bg-white rounded-lg shadow-md overflow-hidden">
                <div class="bg-orange-100 px-4 py-3">
                    <div class="flex justify-between items-center">
                        <h2 class="text-lg font-bold text-gray-800">転出・修了者</h2>
                        <span class="text-xl font-bold text-orange-600">${transferred.length}名</span>
                    </div>
                </div>
                <div class="p-4">
                    <input type="text" id="transferredSearch" placeholder="名前で検索..." 
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg mb-3 focus:outline-none focus:ring-2 focus:ring-orange-500">
                    <div class="overflow-auto custom-scrollbar" style="max-height: 65vh;">
                        <table class="w-full text-sm">
                            <thead class="bg-gray-50 sticky top-0">
                                <tr>
                                    <th class="px-2 py-2 text-left">No.</th>
                                    <th class="px-2 py-2 text-left">名前</th>
                                    <th class="px-2 py-2 text-left">専門科</th>
                                    <th class="px-2 py-2 text-left">転出先</th>
                                </tr>
                            </thead>
                            <tbody id="transferredTable">
                                ${generateTransferredRows(transferred)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <!-- 右カラム: 参照リスト -->
            <div class="bg-white rounded-lg shadow-md overflow-hidden">
                <div class="bg-gray-100 px-4 py-3">
                    <h2 class="text-lg font-bold text-gray-800">参照リスト（元データ）</h2>
                </div>
                <div class="p-4">
                    <input type="text" id="referenceSearch" placeholder="名前で検索..." 
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg mb-3 focus:outline-none focus:ring-2 focus:ring-gray-500">
                    <div class="overflow-auto custom-scrollbar" style="max-height: 65vh;">
                        <table class="w-full text-sm">
                            <thead class="bg-gray-50 sticky top-0">
                                <tr>
                                    <th class="px-2 py-2 text-left">名前</th>
                                    <th class="px-2 py-2 text-left">専門科</th>
                                    <th class="px-2 py-2 text-left">進路</th>
                                    <th class="px-2 py-2 text-left">動向調査</th>
                                </tr>
                            </thead>
                            <tbody id="referenceTable">
                                ${generateReferenceRows(reference)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- フッター集計バー -->
        <div class="bg-white rounded-lg shadow-md p-4">
            <div class="flex justify-center space-x-8 text-sm font-medium">
                <span class="text-blue-600">進級者：${promoted.length}名</span>
                <span class="text-gray-400">｜</span>
                <span class="text-orange-600">転出・修了者：${transferred.length}名</span>
                <span class="text-gray-400">｜</span>
                <span class="text-red-600">除外（中断・退職等）：${excluded.length}名</span>
            </div>
        </div>
    `;
    
    // 検索機能を追加
    setupSearchFilters(promoted, transferred, reference);
}

// 進級者テーブル行を生成
function generatePromotedRows(promoted) {
    if (promoted.length === 0) {
        return '<tr><td colspan="4" class="px-2 py-4 text-center text-gray-500">該当データなし</td></tr>';
    }
    
    return promoted.map((trainee, index) => `
        <tr class="border-b hover:bg-gray-50" data-name="${trainee.name}">
            <td class="px-2 py-2">${index + 1}</td>
            <td class="px-2 py-2 font-medium">${trainee.name}</td>
            <td class="px-2 py-2">${trainee.department}</td>
            <td class="px-2 py-2">${trainee.university}</td>
        </tr>
    `).join('');
}

// 転出・修了者テーブル行を生成
function generateTransferredRows(transferred) {
    if (transferred.length === 0) {
        return '<tr><td colspan="4" class="px-2 py-4 text-center text-gray-500">該当データなし</td></tr>';
    }
    
    return transferred.map((trainee, index) => `
        <tr class="border-b hover:bg-gray-50" data-name="${trainee.name}">
            <td class="px-2 py-2">${index + 1}</td>
            <td class="px-2 py-2 font-medium">${trainee.name}</td>
            <td class="px-2 py-2">${trainee.department}</td>
            <td class="px-2 py-2">${trainee.survey || trainee.course}</td>
        </tr>
    `).join('');
}

// 参照リストテーブル行を生成
function generateReferenceRows(reference) {
    if (reference.length === 0) {
        return '<tr><td colspan="4" class="px-2 py-4 text-center text-gray-500">該当データなし</td></tr>';
    }
    
    return reference.map((trainee) => `
        <tr class="border-b hover:bg-gray-100 ${getReferenceRowColor(trainee)}" data-name="${trainee.name}">
            <td class="px-2 py-2 font-medium">${trainee.name}</td>
            <td class="px-2 py-2">${trainee.department}</td>
            <td class="px-2 py-2">${trainee.course}</td>
            <td class="px-2 py-2">${trainee.survey}</td>
        </tr>
    `).join('');
}

// 検索フィルター機能を設定
function setupSearchFilters(promoted, transferred, reference) {
    // 進級者検索
    const promotedSearch = document.getElementById('promotedSearch');
    promotedSearch.addEventListener('input', (e) => {
        filterTable('promotedTable', e.target.value);
    });
    
    // 転出者検索
    const transferredSearch = document.getElementById('transferredSearch');
    transferredSearch.addEventListener('input', (e) => {
        filterTable('transferredTable', e.target.value);
    });
    
    // 参照リスト検索
    const referenceSearch = document.getElementById('referenceSearch');
    referenceSearch.addEventListener('input', (e) => {
        filterTable('referenceTable', e.target.value);
    });
}

// テーブルをフィルタリング
function filterTable(tableId, searchText) {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tr');
    const searchLower = searchText.toLowerCase();
    
    rows.forEach(row => {
        const name = row.dataset.name;
        if (!name) return;
        
        if (name.toLowerCase().includes(searchLower)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// エラーメッセージを表示
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    errorText.textContent = message;
    errorDiv.classList.remove('hidden');
}

// エラーメッセージを非表示
function hideError() {
    document.getElementById('errorMessage').classList.add('hidden');
}

// ローディングを表示/非表示
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}
