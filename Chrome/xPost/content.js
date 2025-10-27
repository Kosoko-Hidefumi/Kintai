// Content Script for X (Twitter) post injection

// 送信状態を管理
const sentPosts = new Set();

// アイコンのHTMLを作成
function createTransferIcon() {
  const icon = document.createElement('div');
  icon.className = 'xpost-transfer-icon';
  icon.innerHTML = `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <path d="M13 7h8m0 0l-4-4m4 4l-4 4M3 17h8m0 0l-4 4m4-4l-4-4"/>
    </svg>
  `;
  icon.title = 'Slack/Notionに転送';
  icon.style.cssText = `
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    padding: 8px;
    border-radius: 9999px;
    transition: background-color 0.2s;
    margin-right: 12px;
  `;
  
  // ホバーエフェクト
  icon.addEventListener('mouseenter', () => {
    icon.style.backgroundColor = 'rgba(29, 155, 240, 0.1)';
  });
  
  icon.addEventListener('mouseleave', () => {
    icon.style.backgroundColor = 'transparent';
  });
  
  return icon;
}

// 投稿データを取得
function extractPostData(postElement) {
  try {
    // 投稿テキスト
    const textElement = postElement.querySelector('[data-testid="tweetText"]');
    const text = textElement ? textElement.innerText.trim() : '';
    
    // 投稿URL
    const linkElement = postElement.querySelector('a[href*="/status/"]');
    const relativeUrl = linkElement ? linkElement.getAttribute('href') : '';
    const url = relativeUrl.startsWith('http') ? relativeUrl : `https://x.com${relativeUrl}`;
    
    // 投稿者情報
    const authorElement = postElement.querySelector('[data-testid="User-Name"]');
    const author = authorElement ? authorElement.innerText.trim() : 'Unknown User';
    
    // 投稿日時
    const timeElement = postElement.querySelector('time');
    const timestamp = timeElement ? timeElement.getAttribute('datetime') : '';
    
    return { text, url, author, timestamp };
  } catch (error) {
    console.error('Error extracting post data:', error);
    return null;
  }
}

// アイコンの状態を更新
function updateIconState(icon, state) {
  icon.classList.remove('loading', 'success', 'error');
  icon.classList.add(state);
  
  switch (state) {
    case 'loading':
      icon.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style="animation: spin 1s linear infinite;">
          <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="60" stroke-dashoffset="30"/>
        </svg>
      `;
      icon.title = '送信中...';
      break;
      
    case 'success':
      icon.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
          <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
        </svg>
      `;
      icon.style.color = '#00ba7c';
      icon.title = '送信完了';
      break;
      
    case 'error':
      icon.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
          <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
        </svg>
      `;
      icon.style.color = '#f4212e';
      icon.title = '送信失敗';
      break;
  }
  
  if (state !== 'loading') {
    setTimeout(() => {
      icon.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
          <path d="M13 7h8m0 0l-4-4m4 4l-4 4M3 17h8m0 0l-4 4m4-4l-4-4"/>
        </svg>
      `;
      icon.style.color = '';
      icon.title = 'Slack/Notionに転送';
      icon.classList.remove('loading', 'success', 'error');
    }, 2000);
  }
}

// 投稿をSlackに送信
async function sendToSlack(postData) {
  try {
    updateIconState(event.target, 'loading');
    
    chrome.runtime.sendMessage(
      { action: 'sendToSlack', data: postData },
      (response) => {
        if (response && response.success) {
          updateIconState(event.target, 'success');
        } else {
          updateIconState(event.target, 'error');
          console.error('Slack送信エラー:', response?.error);
        }
      }
    );
  } catch (error) {
    updateIconState(event.target, 'error');
    console.error('送信エラー:', error);
  }
}

// 投稿をNotionに追加
async function addToNotion(postData) {
  try {
    updateIconState(event.target, 'loading');
    
    chrome.runtime.sendMessage(
      { action: 'addToNotion', data: postData },
      (response) => {
        if (response && response.success) {
          updateIconState(event.target, 'success');
        } else {
          updateIconState(event.target, 'error');
          console.error('Notion追加エラー:', response?.error);
        }
      }
    );
  } catch (error) {
    updateIconState(event.target, 'error');
    console.error('追加エラー:', error);
  }
}

// アイコンにクリックイベントを追加
function attachIconListener(icon, postElement) {
  icon.addEventListener('click', async (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const postData = extractPostData(postElement);
    if (!postData) {
      alert('投稿データの取得に失敗しました');
      return;
    }
    
    // 設定を取得
    chrome.storage.local.get(['config'], async (result) => {
      const config = result.config || {};
      
      // Slack設定があればSlackに、Notion設定があればNotionに送信
      // 両方ある場合は両方送信
      const promises = [];
      
      if (config.slackToken && config.slackChannelId) {
        promises.push(new Promise(resolve => {
          chrome.runtime.sendMessage({ action: 'sendToSlack', data: postData }, resolve);
        }));
      }
      
      if (config.notionToken && config.notionDatabaseId) {
        promises.push(new Promise(resolve => {
          chrome.runtime.sendMessage({ action: 'addToNotion', data: postData }, resolve);
        }));
      }
      
      if (promises.length === 0) {
        alert('設定画面でSlackまたはNotionの設定を行ってください');
        chrome.runtime.sendMessage({ action: 'openPopup' });
        return;
      }
      
      // すべての送信を実行
      Promise.all(promises).then(results => {
        const allSuccess = results.every(r => r && r.success);
        if (allSuccess) {
          updateIconState(e.target, 'success');
        } else {
          updateIconState(e.target, 'error');
        }
      });
    });
    
    // アイコンの状態管理
    const icon = e.target.closest('.xpost-transfer-icon');
    if (icon) {
      const postId = postElement.querySelector('a[href*="/status/"]')?.getAttribute('href');
      if (postId && sentPosts.has(postId)) {
        return; // 既に送信済み
      }
      
      if (postId) {
        sentPosts.add(postId);
      }
    }
  });
}

// アイコンを投稿に追加
function addIconToPost(postElement) {
  // 既にアイコンが追加されている場合はスキップ
  if (postElement.querySelector('.xpost-transfer-icon')) {
    return;
  }
  
  // アクションボタンの親要素を探す
  const actionBar = postElement.querySelector('[role="group"]');
  if (!actionBar) {
    return;
  }
  
  const icon = createTransferIcon();
  attachIconListener(icon, postElement);
  
  // ブックマークアイコンの前に挿入
  const bookmarkButton = postElement.querySelector('[data-testid="bookmark"]');
  if (bookmarkButton) {
    bookmarkButton.parentElement.insertBefore(icon, bookmarkButton.parentElement.firstChild);
  } else {
    // ブックマークが見つからない場合は最後に追加
    actionBar.appendChild(icon);
  }
}

// 全ての投稿をスキャン
function scanAndInjectIcons() {
  // Xの投稿コンテナを検索（複数のバージョンに対応）
  const posts = document.querySelectorAll('[data-testid="tweet"]');
  
  posts.forEach(post => {
    addIconToPost(post);
  });
}

// 初期スキャン
setTimeout(() => {
  scanAndInjectIcons();
}, 1000);

// 無限スクロールに対応
const observer = new MutationObserver((mutations) => {
  scanAndInjectIcons();
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

// CSSスタイルを追加
const style = document.createElement('style');
style.textContent = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .xpost-transfer-icon.loading {
    opacity: 0.7;
  }
  
  .xpost-transfer-icon.success {
    opacity: 1;
  }
  
  .xpost-transfer-icon.error {
    opacity: 0.9;
  }
`;
document.head.appendChild(style);

