// Background Service Worker for X Post Extension

// デフォルト設定
const DEFAULT_CONFIG = {
  slackToken: '',
  slackChannelId: '',
  notionToken: '',
  notionDatabaseId: ''
};

// 拡張機能のインストール時
chrome.runtime.onInstalled.addListener(() => {
  console.log('X Post Extension installed');
  
  // デフォルト設定を保存
  chrome.storage.local.get(['config'], (result) => {
    if (!result.config) {
      chrome.storage.local.set({ config: DEFAULT_CONFIG });
    }
  });
});

// Slack APIへのメッセージ送信
async function sendToSlack(postData) {
  const { config } = await chrome.storage.local.get(['config']);
  
  if (!config.slackToken || !config.slackChannelId) {
    throw new Error('Slack設定が完了していません');
  }

  const message = formatSlackMessage(postData);
  
  const response = await fetch('https://slack.com/api/chat.postMessage', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${config.slackToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      channel: config.slackChannelId,
      text: message.text,
      blocks: message.blocks
    })
  });

  const result = await response.json();
  
  if (!result.ok) {
    throw new Error(`Slack API Error: ${result.error}`);
  }

  return result;
}

// Notion APIへの投稿追加
async function addToNotion(postData) {
  const { config } = await chrome.storage.local.get(['config']);
  
  if (!config.notionToken || !config.notionDatabaseId) {
    throw new Error('Notion設定が完了していません');
  }

  const pageData = formatNotionPage(postData, config.notionDatabaseId);
  
  const response = await fetch('https://api.notion.com/v1/pages', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${config.notionToken}`,
      'Content-Type': 'application/json',
      'Notion-Version': '2022-06-28'
    },
    body: JSON.stringify(pageData)
  });

  const result = await response.json();
  
  if (response.status !== 200 && response.status !== 201) {
    throw new Error(`Notion API Error: ${JSON.stringify(result)}`);
  }

  return result;
}

// Slackメッセージのフォーマット
function formatSlackMessage(postData) {
  const text = `*${postData.author}*\n${postData.text}\n\n<${postData.url}|元の投稿を見る>`;
  
  const blocks = [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": `*${postData.author}*\n${postData.text}`
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": `<${postData.url}|元の投稿を見る>`
      }
    }
  ];

  if (postData.timestamp) {
    blocks.push({
      "type": "context",
      "elements": [
        {
          "type": "mrkdwn",
          "text": `投稿日時: ${postData.timestamp}`
        }
      ]
    });
  }

  return { text, blocks };
}

// Notionページのフォーマット
function formatNotionPage(postData, databaseId) {
  return {
    parent: {
      database_id: databaseId
    },
    properties: {
      'Title': {
        title: [
          {
            text: {
              content: postData.text.substring(0, 100) || 'X投稿'
            }
          }
        ]
      },
      'Content': {
        rich_text: [
          {
            text: {
              content: postData.text
            }
          }
        ]
      },
      'URL': {
        url: postData.url
      },
      'Author': {
        rich_text: [
          {
            text: {
              content: postData.author
            }
          }
        ]
      },
      'Timestamp': {
        date: {
          start: postData.timestamp || new Date().toISOString()
        }
      }
    }
  };
}

// Content Scriptからのメッセージを受信
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'sendToSlack') {
    sendToSlack(request.data)
      .then(result => {
        sendResponse({ success: true, result });
      })
      .catch(error => {
        sendResponse({ success: false, error: error.message });
      });
    return true; // 非同期応答
  }

  if (request.action === 'addToNotion') {
    addToNotion(request.data)
      .then(result => {
        sendResponse({ success: true, result });
      })
      .catch(error => {
        sendResponse({ success: false, error: error.message });
      });
    return true; // 非同期応答
  }

  if (request.action === 'getConfig') {
    chrome.storage.local.get(['config'], (result) => {
      sendResponse({ config: result.config || DEFAULT_CONFIG });
    });
    return true;
  }
});


