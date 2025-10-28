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
    position: relative;
    display: inline-flex !important;
    visibility: visible !important;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    padding: 8px;
    border-radius: 9999px;
    transition: background-color 0.2s;
    margin-right: 12px;
    z-index: 9999;
    color: rgb(83, 100, 113);
    background-color: transparent;
  `;
  
  // ホバーエフェクト
  icon.addEventListener('mouseenter', () => {
    icon.style.backgroundColor = 'rgba(29, 155, 240, 0.1)';
    icon.style.color = 'rgb(29, 155, 240)';
  });
  
  icon.addEventListener('mouseleave', () => {
    icon.style.backgroundColor = 'transparent';
    icon.style.color = 'rgb(83, 100, 113)';
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
  
  console.log('[XPost] 投稿要素を検証中...', postElement);
  
  // アクションボタンの親要素を探す（複数のパターンを試す）
  let actionBar = postElement.querySelector('[role="group"]');
  
  // 代替1: データテストIDで探す
  if (!actionBar) {
    const bookmark = postElement.querySelector('[data-testid="bookmark"]');
    if (bookmark) {
      actionBar = bookmark.parentElement;
      console.log('[XPost] ブックマークの親要素を使用');
    }
  }
  
  // 代替2: いいねボタンから探す
  if (!actionBar) {
    const like = postElement.querySelector('[data-testid="like"]');
    if (like) {
      actionBar = like.closest('[role="group"]');
      if (!actionBar) {
        actionBar = like.parentElement;
      }
      console.log('[XPost] いいねボタンから親要素を特定');
    }
  }
  
  // 代替3: articleの最後のdiv
  if (!actionBar) {
    const allGroups = postElement.querySelectorAll('[role="group"]');
    actionBar = allGroups[allGroups.length - 1];
    if (actionBar) console.log('[XPost] 最後のグループ要素を使用');
  }
  
  // 代替4: タッチ操作エリアを探す
  if (!actionBar) {
    const buttons = postElement.querySelectorAll('button');
    const lastButton = buttons[buttons.length - 1];
    if (lastButton) {
      actionBar = lastButton.parentElement;
      console.log('[XPost] 最後のボタンの親要素を使用');
    }
  }
  
  if (!actionBar) {
    console.error('[XPost] アクションバーが見つかりません。DOM構造:', postElement);
    return;
  }
  
  console.log('[XPost] アクションバーを発見:', actionBar);
  console.log('[XPost] アクションバーの子要素数:', actionBar.children.length);
  
  const icon = createTransferIcon();
  attachIconListener(icon, postElement);
  
  // XのUIを分析して最適な挿入位置を探す
  console.log('[XPost] アクションバーの構造を分析中...');
  console.log('[XPost] アクションバー:', actionBar);
  console.log('[XPost] アクションバーの子要素:', Array.from(actionBar.children));
  
  const bookmarkButton = postElement.querySelector('[data-testid="bookmark"]');
  const likeButton = postElement.querySelector('[data-testid="like"]');
  const shareButton = postElement.querySelector('[data-testid="share"]');
  
  console.log('[XPost] ブックマークボタン:', bookmarkButton);
  console.log('[XPost] いいねボタン:', likeButton);
  console.log('[XPost] シェアボタン:', shareButton);
  
  let inserted = false;
  
  // 戦略1: ブックマークボタンの親に直接挿入
  if (bookmarkButton && bookmarkButton.parentElement) {
    try {
      bookmarkButton.parentElement.insertBefore(icon, bookmarkButton);
      console.log('[XPost] insertBefore実行完了');
      // すぐに確認
      if (postElement.contains(icon)) {
        inserted = true;
        console.log('[XPost] アイコンをブックマークの直前に追加（成功・確認済み）');
      } else {
        console.error('[XPost] アイコンが追加されませんでした（確認失敗）');
      }
    } catch (e) {
      console.error('[XPost] ブックマーク前の挿入エラー:', e);
    }
  }
  
  // 戦略2: いいねボタンの親に挿入
  if (!inserted && likeButton && likeButton.parentElement) {
    try {
      likeButton.parentElement.insertBefore(icon, likeButton);
      console.log('[XPost] いいねボタン前にinsertBefore実行');
      if (postElement.contains(icon)) {
        inserted = true;
        console.log('[XPost] アイコンをいいねボタンの直前に追加（成功・確認済み）');
      }
    } catch (e) {
      console.error('[XPost] いいねボタン前の挿入エラー:', e);
    }
  }
  
  // 戦略3: アクションバーの最初に追加
  if (!inserted) {
    try {
      actionBar.insertBefore(icon, actionBar.firstChild);
      console.log('[XPost] 先頭にinsertBefore実行');
      if (postElement.contains(icon)) {
        inserted = true;
        console.log('[XPost] アイコンをアクションバーの先頭に追加（成功・確認済み）');
      }
    } catch (e) {
      console.error('[XPost] 先頭への挿入エラー:', e);
    }
  }
  
  // 戦略4: appendChildで追加
  if (!inserted) {
    try {
      actionBar.appendChild(icon);
      console.log('[XPost] appendChild実行');
      if (postElement.contains(icon)) {
        inserted = true;
        console.log('[XPost] アイコンをappendChildで追加（成功・確認済み）');
      }
    } catch (e) {
      console.error('[XPost] appendChildエラー:', e);
    }
  }
  
  // 最終確認
  if (!inserted) {
    console.error('[XPost] 全ての挿入戦略が失敗しました');
    console.error('[XPost] デバッグ: actionBarの詳細:', actionBar);
    console.error('[XPost] デバッグ: postElementの詳細:', postElement);
    // 強制的に追加（最後の手段）
    try {
      document.body.appendChild(icon);
      console.log('[XPost] デバッグ: bodyに強制的に追加');
    } catch (e) {
      console.error('[XPost] body追加も失敗:', e);
    }
  }
  
  // アイコンが実際にDOMに追加されたか確認
  setTimeout(() => {
    const checkIcon = postElement.querySelector('.xpost-transfer-icon');
    if (checkIcon && document.body.contains(checkIcon)) {
      console.log('[XPost] アイコンがDOMに追加されました');
      const rect = checkIcon.getBoundingClientRect();
      console.log('[XPost] アイコンの位置:', rect);
      console.log('[XPost] アイコンのスタイル:', window.getComputedStyle(checkIcon));
      
      // 親要素の情報も表示
      console.log('[XPost] 親要素:', checkIcon.parentElement);
      console.log('[XPost] 親要素のスタイル:', window.getComputedStyle(checkIcon.parentElement));
      
      if (rect.width === 0 || rect.height === 0) {
        console.warn('[XPost] アイコンがサイズ0です。スタイルを確認してください');
      } else {
        console.log('[XPost] アイコンのサイズ: width=' + rect.width + ', height=' + rect.height);
        console.log('[XPost] 画面上の位置: x=' + rect.x + ', y=' + rect.y);
      }
    } else {
      console.error('[XPost] アイコンがDOMに追加されていません');
    }
  }, 100);
}

// 全ての投稿をスキャン
function scanAndInjectIcons() {
  // Xの投稿コンテナを検索（複数のバージョンに対応）
  let posts = document.querySelectorAll('[data-testid="tweet"]');
  
  console.log(`[XPost] 投稿数 (tweet): ${posts.length}`);
  
  // 代替セレクター: article要素
  if (posts.length === 0) {
    posts = document.querySelectorAll('article');
    console.log(`[XPost] 投稿数 (article): ${posts.length}`);
  }
  
  // さらに別のパターン: role="article"
  if (posts.length === 0) {
    posts = document.querySelectorAll('[role="article"]');
    console.log(`[XPost] 投稿数 (role=article): ${posts.length}`);
  }
  
  posts.forEach((post, index) => {
    console.log(`[XPost] 投稿 ${index + 1} を処理中...`);
    addIconToPost(post);
  });
}

// 初期スキャン
console.log('[XPost] Content script loaded');
console.log('[XPost] Current URL:', window.location.href);

// DOMContentLoadedが完了した後にスキャン
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log('[XPost] DOM ready');
    setTimeout(() => {
      console.log('[XPost] Starting initial scan...');
      scanAndInjectIcons();
    }, 1000);
  });
} else {
  console.log('[XPost] DOM already loaded');
  setTimeout(() => {
    console.log('[XPost] Starting initial scan...');
    scanAndInjectIcons();
  }, 1000);
}

// 無限スクロールに対応
const observer = new MutationObserver((mutations) => {
  scanAndInjectIcons();
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

// ページの読み込み完了を待つ
window.addEventListener('load', () => {
  console.log('[XPost] Window loaded');
  setTimeout(() => {
    scanAndInjectIcons();
  }, 2000);
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
