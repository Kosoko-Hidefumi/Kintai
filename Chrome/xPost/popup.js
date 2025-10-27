// Popup UI JavaScript for X Post Extension

// DOM要素の取得
const slackTokenInput = document.getElementById('slack-token');
const slackChannelInput = document.getElementById('slack-channel');
const notionTokenInput = document.getElementById('notion-token');
const notionDatabaseInput = document.getElementById('notion-database');
const saveBtn = document.getElementById('save-btn');
const resetBtn = document.getElementById('reset-btn');
const testSlackBtn = document.getElementById('test-slack');
const testNotionBtn = document.getElementById('test-notion');
const statusMessage = document.getElementById('status-message');

// 設定をロード
function loadSettings() {
  chrome.storage.local.get(['config'], (result) => {
    const config = result.config || {};
    
    if (config.slackToken) slackTokenInput.value = config.slackToken;
    if (config.slackChannelId) slackChannelInput.value = config.slackChannelId;
    if (config.notionToken) notionTokenInput.value = config.notionToken;
    if (config.notionDatabaseId) notionDatabaseInput.value = config.notionDatabaseId;
  });
}

// 設定を保存
function saveSettings() {
  const config = {
    slackToken: slackTokenInput.value.trim(),
    slackChannelId: slackChannelInput.value.trim(),
    notionToken: notionTokenInput.value.trim(),
    notionDatabaseId: notionDatabaseInput.value.trim()
  };
  
  chrome.storage.local.set({ config }, () => {
    showStatus('設定を保存しました', 'success');
    setTimeout(() => {
      hideStatus();
    }, 3000);
  });
}

// 設定をリセット
function resetSettings() {
  if (confirm('設定をリセットしますか？')) {
    chrome.storage.local.set({ config: {} }, () => {
      slackTokenInput.value = '';
      slackChannelInput.value = '';
      notionTokenInput.value = '';
      notionDatabaseInput.value = '';
      showStatus('設定をリセットしました', 'info');
      setTimeout(() => {
        hideStatus();
      }, 3000);
    });
  }
}

// Slack送信をテスト
function testSlackConnection() {
  const config = {
    slackToken: slackTokenInput.value.trim(),
    slackChannelId: slackChannelInput.value.trim()
  };
  
  if (!config.slackToken || !config.slackChannelId) {
    showStatus('Slack設定を入力してください', 'error');
    return;
  }
  
  // テスト用の投稿データ
  const testData = {
    text: 'テスト投稿 - X Post Extension',
    url: 'https://example.com/test',
    author: 'Test User',
    timestamp: new Date().toISOString()
  };
  
  showStatus('送信テスト中...', 'info');
  
  chrome.runtime.sendMessage({
    action: 'sendToSlack',
    data: testData
  }, (response) => {
    if (response && response.success) {
      showStatus('Slack送信テスト成功！', 'success');
    } else {
      showStatus(`Slack送信テスト失敗: ${response?.error || 'Unknown error'}`, 'error');
    }
  });
}

// Notion追加をテスト
function testNotionConnection() {
  const config = {
    notionToken: notionTokenInput.value.trim(),
    notionDatabaseId: notionDatabaseInput.value.trim()
  };
  
  if (!config.notionToken || !config.notionDatabaseId) {
    showStatus('Notion設定を入力してください', 'error');
    return;
  }
  
  // テスト用の投稿データ
  const testData = {
    text: 'テスト投稿 - X Post Extension',
    url: 'https://example.com/test',
    author: 'Test User',
    timestamp: new Date().toISOString()
  };
  
  showStatus('追加テスト中...', 'info');
  
  chrome.runtime.sendMessage({
    action: 'addToNotion',
    data: testData
  }, (response) => {
    if (response && response.success) {
      showStatus('Notion追加テスト成功！', 'success');
    } else {
      showStatus(`Notion追加テスト失敗: ${response?.error || 'Unknown error'}`, 'error');
    }
  });
}

// ステータスメッセージを表示
function showStatus(message, type) {
  statusMessage.textContent = message;
  statusMessage.className = `status-message show ${type}`;
}

// ステータスメッセージを非表示
function hideStatus() {
  statusMessage.classList.remove('show');
}

// イベントリスナーの追加
saveBtn.addEventListener('click', saveSettings);
resetBtn.addEventListener('click', resetSettings);
testSlackBtn.addEventListener('click', testSlackConnection);
testNotionBtn.addEventListener('click', testNotionConnection);

// 初期化
loadSettings();

