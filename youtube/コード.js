/**
 * YouTube競合チャンネル分析ツール
 * 
 * @description 競合YouTubeチャンネルの情報と動画データを自動収集し、スプレッドシートに一元管理するツール
 * @author Your Name
 * @version 1.0.0
 * @created 2025-11-07
 * 
 * 必要な設定:
 * - Apps Scriptエディタで「サービス」からYouTube Data API v3を追加
 */

// ============================================================
// 定数定義
// ============================================================

/** シート名の定数 */
const SHEET_NAMES = {
  SETTINGS: '設定',
  CHANNEL_LIST: 'チャンネルリスト',
  CHANNEL_INFO: 'チャンネル情報',
  VIDEO_INFO: '動画情報'
};

/** デフォルト設定値 */
const DEFAULT_SETTINGS = {
  MAX_VIDEOS: 50  // 1チャンネルあたりの取得動画数
};

/** ヘッダー行の定義 */
const HEADERS = {
  SETTINGS: ['設定項目', '値'],
  CHANNEL_LIST: ['チャンネルID', 'メモ', '有効'],
  CHANNEL_INFO: [
    '取得日時', 'チャンネルID', 'チャンネル名', '登録者数', '総視聴回数',
    '動画数', '開設日', 'カスタムURL', '説明文', '国', 'サムネイルURL', 'チャンネルURL'
  ],
  VIDEO_INFO: [
    '取得日時', 'チャンネル名', 'チャンネルID', '動画ID', '動画タイトル',
    '公開日時', '視聴回数', '高評価数', 'コメント数', '再生時間（秒）',
    '再生時間（表示）', 'タグ', 'カテゴリID', '説明文', 'サムネイルURL', '動画URL'
  ]
};

/** ヘッダー行の背景色 */
const HEADER_COLOR = '#4A86E8';

// ============================================================
// カスタムメニュー機能
// ============================================================

/**
 * スプレッドシートを開いたときに自動実行される関数
 * カスタムメニューを追加する
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  
  ui.createMenu('📊 YouTube分析')
    .addItem('📺 チャンネル情報を取得', 'menuFetchChannelInfo')
    .addItem('🎬 動画情報を取得', 'menuFetchVideoInfo')
    .addItem('🔄 すべて実行', 'menuFetchAll')
    .addSeparator()
    .addItem('🗑️ データをクリア', 'menuClearData')
    .addSeparator()
    .addItem('⚙️ 初期セットアップ', 'setupSpreadsheet')
    .addToUi();
  
  Logger.log('カスタムメニューを追加しました');
}

// ============================================================
// 初期セットアップ関数
// ============================================================

/**
 * スプレッドシートの初期セットアップを行う
 * 必要なシートとヘッダー行を作成し、基本設定を行う
 */
function setupSpreadsheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  try {
    // 既存のシートを取得または作成
    setupSettingsSheet(ss);
    setupChannelListSheet(ss);
    setupChannelInfoSheet(ss);
    setupVideoInfoSheet(ss);
    
    SpreadsheetApp.getUi().alert(
      '✅ セットアップ完了',
      '必要なシートとヘッダーが作成されました。\n\n' +
      '次の手順:\n' +
      '1. Apps Scriptエディタで「サービス」からYouTube Data API v3を追加\n' +
      '2. 「チャンネルリスト」シートに競合チャンネルIDを入力\n' +
      '3. メニューから「チャンネル情報を取得」を実行',
      SpreadsheetApp.getUi().ButtonSet.OK
    );
  } catch (error) {
    Logger.log('セットアップエラー: ' + error.toString());
    SpreadsheetApp.getUi().alert('❌ エラー', 'セットアップ中にエラーが発生しました:\n' + error.message, SpreadsheetApp.getUi().ButtonSet.OK);
  }
}

/**
 * 「設定」シートをセットアップ
 */
function setupSettingsSheet(ss) {
  let sheet = ss.getSheetByName(SHEET_NAMES.SETTINGS);
  
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAMES.SETTINGS, 0);
  }
  
  // ヘッダー行を設定
  const headerRange = sheet.getRange(1, 1, 1, HEADERS.SETTINGS.length);
  headerRange.setValues([HEADERS.SETTINGS]);
  headerRange.setBackground(HEADER_COLOR);
  headerRange.setFontColor('#FFFFFF');
  headerRange.setFontWeight('bold');
  
  // 初期設定値を入力（既存の値がない場合のみ）
  if (sheet.getLastRow() < 2) {
    const settings = [
      ['取得動画数', DEFAULT_SETTINGS.MAX_VIDEOS]
    ];
    sheet.getRange(2, 1, settings.length, 2).setValues(settings);
  }
  
  // 列幅を調整
  sheet.setColumnWidth(1, 200);
  sheet.setColumnWidth(2, 150);
  
  Logger.log('「設定」シートのセットアップ完了');
}

/**
 * 「チャンネルリスト」シートをセットアップ
 */
function setupChannelListSheet(ss) {
  let sheet = ss.getSheetByName(SHEET_NAMES.CHANNEL_LIST);
  
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAMES.CHANNEL_LIST, 1);
  }
  
  // ヘッダー行を設定
  const headerRange = sheet.getRange(1, 1, 1, HEADERS.CHANNEL_LIST.length);
  headerRange.setValues([HEADERS.CHANNEL_LIST]);
  headerRange.setBackground(HEADER_COLOR);
  headerRange.setFontColor('#FFFFFF');
  headerRange.setFontWeight('bold');
  
  // C列をチェックボックス形式に設定（サンプル行を追加）
  if (sheet.getLastRow() < 2) {
    const sampleData = [
      ['', '（例）競合Aチャンネル', true],
      ['', '（例）競合Bチャンネル', false]
    ];
    sheet.getRange(2, 1, sampleData.length, 3).setValues(sampleData);
  }
  
  // 列幅を調整
  sheet.setColumnWidth(1, 250);
  sheet.setColumnWidth(2, 200);
  sheet.setColumnWidth(3, 80);
  
  // データ検証（チェックボックス）をC列に設定
  const checkboxRange = sheet.getRange(2, 3, 100, 1);
  const rule = SpreadsheetApp.newDataValidation().requireCheckbox().build();
  checkboxRange.setDataValidation(rule);
  
  Logger.log('「チャンネルリスト」シートのセットアップ完了');
}

/**
 * 「チャンネル情報」シートをセットアップ
 */
function setupChannelInfoSheet(ss) {
  let sheet = ss.getSheetByName(SHEET_NAMES.CHANNEL_INFO);
  
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAMES.CHANNEL_INFO, 2);
  }
  
  // ヘッダー行を設定
  const headerRange = sheet.getRange(1, 1, 1, HEADERS.CHANNEL_INFO.length);
  headerRange.setValues([HEADERS.CHANNEL_INFO]);
  headerRange.setBackground(HEADER_COLOR);
  headerRange.setFontColor('#FFFFFF');
  headerRange.setFontWeight('bold');
  
  // 列幅を調整
  const columnWidths = [150, 200, 200, 100, 120, 80, 100, 150, 300, 80, 200, 250];
  columnWidths.forEach((width, index) => {
    sheet.setColumnWidth(index + 1, width);
  });
  
  // 行を固定
  sheet.setFrozenRows(1);
  
  Logger.log('「チャンネル情報」シートのセットアップ完了');
}

/**
 * 「動画情報」シートをセットアップ
 */
function setupVideoInfoSheet(ss) {
  let sheet = ss.getSheetByName(SHEET_NAMES.VIDEO_INFO);
  
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAMES.VIDEO_INFO, 3);
  }
  
  // ヘッダー行を設定
  const headerRange = sheet.getRange(1, 1, 1, HEADERS.VIDEO_INFO.length);
  headerRange.setValues([HEADERS.VIDEO_INFO]);
  headerRange.setBackground(HEADER_COLOR);
  headerRange.setFontColor('#FFFFFF');
  headerRange.setFontWeight('bold');
  
  // 列幅を調整
  const columnWidths = [150, 150, 200, 120, 300, 150, 100, 100, 100, 100, 100, 200, 80, 300, 200, 250];
  columnWidths.forEach((width, index) => {
    sheet.setColumnWidth(index + 1, width);
  });
  
  // 行を固定
  sheet.setFrozenRows(1);
  
  Logger.log('「動画情報」シートのセットアップ完了');
}

// ============================================================
// 設定読み込み関数
// ============================================================

/**
 * 設定シートから取得動画数を取得
 * @returns {number} 取得動画数
 */
function getMaxVideos() {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(SHEET_NAMES.SETTINGS);
    
    if (!sheet) {
      Logger.log('設定シートが見つかりません。デフォルト値を使用します。');
      return DEFAULT_SETTINGS.MAX_VIDEOS;
    }
    
    const data = sheet.getDataRange().getValues();
    
    // 「取得動画数」の設定を探す
    for (let i = 1; i < data.length; i++) {
      if (data[i][0] === '取得動画数') {
        const value = parseInt(data[i][1]);
        if (!isNaN(value) && value > 0 && value <= 50) {
          return value;
        }
      }
    }
    
    return DEFAULT_SETTINGS.MAX_VIDEOS;
  } catch (error) {
    Logger.log('設定読み込みエラー: ' + error.toString());
    return DEFAULT_SETTINGS.MAX_VIDEOS;
  }
}

/**
 * シートが存在するか確認
 * @param {string} sheetName - シート名
 * @returns {boolean} シートが存在する場合true
 */
function isSheetExists(sheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  return ss.getSheetByName(sheetName) !== null;
}

/**
 * 全ての必要なシートが存在するか確認
 * @returns {boolean} 全てのシートが存在する場合true
 */
function checkAllSheetsExist() {
  const requiredSheets = Object.values(SHEET_NAMES);
  
  for (const sheetName of requiredSheets) {
    if (!isSheetExists(sheetName)) {
      return false;
    }
  }
  
  return true;
}

// ============================================================
// ユーティリティ関数
// ============================================================

/**
 * 進捗メッセージを表示
 * @param {string} message - 表示するメッセージ
 */
function showProgress(message) {
  Logger.log(message);
  try {
    SpreadsheetApp.getActiveSpreadsheet().toast(message, 'YouTube分析ツール', 3);
  } catch (error) {
    // Toast通知が失敗してもログには記録される
    Logger.log('Toast通知エラー: ' + error.toString());
  }
}

// ============================================================
// チャンネルリスト読み込み機能
// ============================================================

/**
 * チャンネルリストシートから有効なチャンネルIDを取得
 * @returns {Array<Object>} チャンネル情報の配列 [{id: string, memo: string}, ...]
 */
function getActiveChannelIds() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(SHEET_NAMES.CHANNEL_LIST);
  
  if (!sheet) {
    throw new Error('「チャンネルリスト」シートが見つかりません。セットアップを実行してください。');
  }
  
  const lastRow = sheet.getLastRow();
  if (lastRow < 2) {
    throw new Error('チャンネルリストが空です。「チャンネルリスト」シートにチャンネルIDを入力してください。');
  }
  
  const data = sheet.getRange(2, 1, lastRow - 1, 3).getValues();
  const activeChannels = [];
  
  for (let i = 0; i < data.length; i++) {
    const channelId = data[i][0] ? data[i][0].toString().trim() : '';
    const memo = data[i][1] ? data[i][1].toString() : '';
    const isActive = data[i][2] === true;
    
    // チャンネルIDが空でなく、有効にチェックされている場合のみ追加
    if (channelId && isActive) {
      activeChannels.push({
        id: channelId,
        memo: memo
      });
    }
  }
  
  if (activeChannels.length === 0) {
    throw new Error('有効なチャンネルが見つかりません。「チャンネルリスト」で有効にチェックを入れてください。');
  }
  
  Logger.log(`有効なチャンネル数: ${activeChannels.length}`);
  return activeChannels;
}

// ============================================================
// YouTube Data API - チャンネル情報取得
// ============================================================

/**
 * YouTube Data APIでチャンネル情報を取得
 * @param {string} channelId - YouTubeチャンネルID
 * @returns {Object|null} チャンネル情報オブジェクト、エラー時はnull
 */
function getChannelInfo(channelId) {
  try {
    // YouTube Data API v3を使用してチャンネル情報を取得
    const response = YouTube.Channels.list('snippet,statistics,contentDetails', {
      id: channelId
    });
    
    if (!response.items || response.items.length === 0) {
      Logger.log(`チャンネルが見つかりません: ${channelId}`);
      return null;
    }
    
    const channel = response.items[0];
    Logger.log(`チャンネル取得成功: ${channel.snippet.title}`);
    
    return channel;
  } catch (error) {
    Logger.log(`チャンネル情報取得エラー (${channelId}): ${error.toString()}`);
    return null;
  }
}

/**
 * APIレスポンスからチャンネルデータを整形
 * @param {Object} channel - YouTube APIのチャンネルオブジェクト
 * @returns {Array} スプレッドシート用の1行データ配列
 */
function formatChannelData(channel) {
  const now = new Date();
  const snippet = channel.snippet;
  const statistics = channel.statistics;
  
  // チャンネルURLを生成
  const channelUrl = `https://www.youtube.com/channel/${channel.id}`;
  
  // カスタムURLを取得（存在する場合）
  const customUrl = snippet.customUrl || '';
  
  // 開設日を日付オブジェクトに変換
  const publishedAt = snippet.publishedAt ? new Date(snippet.publishedAt) : '';
  
  return [
    now,                                          // 取得日時
    channel.id,                                   // チャンネルID
    snippet.title || '',                          // チャンネル名
    parseInt(statistics.subscriberCount) || 0,   // 登録者数
    parseInt(statistics.viewCount) || 0,         // 総視聴回数
    parseInt(statistics.videoCount) || 0,        // 動画数
    publishedAt,                                  // 開設日
    customUrl,                                    // カスタムURL
    snippet.description || '',                    // 説明文
    snippet.country || '',                        // 国
    snippet.thumbnails?.high?.url || '',         // サムネイルURL
    channelUrl                                    // チャンネルURL
  ];
}

/**
 * チャンネル情報をスプレッドシートに書き込み
 * @param {Array<Array>} channelDataArray - チャンネルデータの2次元配列
 */
function writeChannelInfo(channelDataArray) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(SHEET_NAMES.CHANNEL_INFO);
  
  if (!sheet) {
    throw new Error('「チャンネル情報」シートが見つかりません。');
  }
  
  // 既存のデータをクリア（ヘッダー行を除く）
  const lastRow = sheet.getLastRow();
  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).clear();
  }
  
  // データが空の場合は終了
  if (channelDataArray.length === 0) {
    Logger.log('書き込むチャンネルデータがありません。');
    return;
  }
  
  // データを書き込み
  const range = sheet.getRange(2, 1, channelDataArray.length, channelDataArray[0].length);
  range.setValues(channelDataArray);
  
  // 数値フォーマットを適用
  sheet.getRange(2, 4, channelDataArray.length, 1).setNumberFormat('#,##0');  // 登録者数
  sheet.getRange(2, 5, channelDataArray.length, 1).setNumberFormat('#,##0');  // 総視聴回数
  sheet.getRange(2, 6, channelDataArray.length, 1).setNumberFormat('#,##0');  // 動画数
  
  // 日時フォーマットを適用
  sheet.getRange(2, 1, channelDataArray.length, 1).setNumberFormat('yyyy-mm-dd hh:mm:ss');  // 取得日時
  sheet.getRange(2, 7, channelDataArray.length, 1).setNumberFormat('yyyy-mm-dd');  // 開設日
  
  Logger.log(`${channelDataArray.length}件のチャンネル情報を書き込みました。`);
}

// ============================================================
// メイン処理 - チャンネル情報取得
// ============================================================

/**
 * 全チャンネルの情報を取得してスプレッドシートに書き込む
 * メニューから実行される主要な関数
 */
function fetchAllChannelInfo() {
  const startTime = new Date();
  
  try {
    showProgress('チャンネル情報の取得を開始します...');
    
    // シートの存在確認
    if (!checkAllSheetsExist()) {
      throw new Error('必要なシートが揃っていません。セットアップを実行してください。');
    }
    
    // 有効なチャンネルリストを取得
    const channels = getActiveChannelIds();
    showProgress(`${channels.length}件のチャンネルを処理します...`);
    
    const channelDataArray = [];
    let successCount = 0;
    let errorCount = 0;
    
    // 各チャンネルの情報を取得
    for (let i = 0; i < channels.length; i++) {
      const channel = channels[i];
      showProgress(`[${i + 1}/${channels.length}] ${channel.memo || channel.id} を取得中...`);
      
      const channelInfo = getChannelInfo(channel.id);
      
      if (channelInfo) {
        const formattedData = formatChannelData(channelInfo);
        channelDataArray.push(formattedData);
        successCount++;
      } else {
        errorCount++;
        Logger.log(`チャンネル取得失敗: ${channel.id} (${channel.memo})`);
      }
      
      // API制限を避けるため、少し待機
      Utilities.sleep(100);
    }
    
    // データを書き込み
    if (channelDataArray.length > 0) {
      showProgress('データを書き込んでいます...');
      writeChannelInfo(channelDataArray);
    }
    
    // 完了メッセージ
    const endTime = new Date();
    const duration = ((endTime - startTime) / 1000).toFixed(1);
    
    const message = `✅ チャンネル情報取得完了\n\n` +
                    `成功: ${successCount}件\n` +
                    `失敗: ${errorCount}件\n` +
                    `所要時間: ${duration}秒`;
    
    SpreadsheetApp.getUi().alert('完了', message, SpreadsheetApp.getUi().ButtonSet.OK);
    Logger.log(message);
    
  } catch (error) {
    const errorMessage = `❌ エラーが発生しました\n\n${error.message}`;
    SpreadsheetApp.getUi().alert('エラー', errorMessage, SpreadsheetApp.getUi().ButtonSet.OK);
    Logger.log('エラー: ' + error.toString());
    throw error;
  }
}

// ============================================================
// YouTube Data API - 動画情報取得
// ============================================================

/**
 * チャンネルのアップロードプレイリストIDを取得
 * @param {string} channelId - YouTubeチャンネルID
 * @returns {string|null} アップロードプレイリストID、エラー時はnull
 */
function getUploadsPlaylistId(channelId) {
  try {
    const response = YouTube.Channels.list('contentDetails', {
      id: channelId
    });
    
    if (!response.items || response.items.length === 0) {
      Logger.log(`チャンネルが見つかりません: ${channelId}`);
      return null;
    }
    
    const uploadsPlaylistId = response.items[0].contentDetails.relatedPlaylists.uploads;
    Logger.log(`アップロードプレイリストID取得: ${uploadsPlaylistId}`);
    
    return uploadsPlaylistId;
  } catch (error) {
    Logger.log(`プレイリストID取得エラー (${channelId}): ${error.toString()}`);
    return null;
  }
}

/**
 * プレイリストから動画IDのリストを取得
 * @param {string} playlistId - プレイリストID
 * @param {number} maxResults - 取得する最大動画数
 * @returns {Array<string>} 動画IDの配列
 */
function getVideoIdsFromPlaylist(playlistId, maxResults) {
  try {
    const videoIds = [];
    let pageToken = null;
    
    do {
      const options = {
        playlistId: playlistId,
        maxResults: Math.min(maxResults - videoIds.length, 50),
        pageToken: pageToken
      };
      
      const response = YouTube.PlaylistItems.list('contentDetails', options);
      
      if (response.items) {
        for (const item of response.items) {
          videoIds.push(item.contentDetails.videoId);
          if (videoIds.length >= maxResults) {
            break;
          }
        }
      }
      
      pageToken = response.nextPageToken;
      
      // 指定数に達したら終了
      if (videoIds.length >= maxResults) {
        break;
      }
      
    } while (pageToken);
    
    Logger.log(`${videoIds.length}件の動画IDを取得しました`);
    return videoIds;
    
  } catch (error) {
    Logger.log(`動画IDリスト取得エラー (${playlistId}): ${error.toString()}`);
    return [];
  }
}

/**
 * 動画IDのリストから詳細情報を取得（50件ずつバッチ処理）
 * @param {Array<string>} videoIds - 動画IDの配列
 * @returns {Array<Object>} 動画情報オブジェクトの配列
 */
function getVideosInfo(videoIds) {
  try {
    const videos = [];
    
    // 50件ずつバッチで処理
    for (let i = 0; i < videoIds.length; i += 50) {
      const batchIds = videoIds.slice(i, i + 50);
      const idsString = batchIds.join(',');
      
      const response = YouTube.Videos.list('snippet,statistics,contentDetails', {
        id: idsString
      });
      
      if (response.items) {
        videos.push(...response.items);
      }
      
      // API制限を避けるため少し待機
      if (i + 50 < videoIds.length) {
        Utilities.sleep(100);
      }
    }
    
    Logger.log(`${videos.length}件の動画詳細情報を取得しました`);
    return videos;
    
  } catch (error) {
    Logger.log(`動画詳細情報取得エラー: ${error.toString()}`);
    return [];
  }
}

/**
 * ISO 8601形式の再生時間を秒数に変換
 * @param {string} isoDuration - ISO 8601形式の時間（例: PT1H2M3S）
 * @returns {number} 秒数
 */
function parseDuration(isoDuration) {
  if (!isoDuration) return 0;
  
  const matches = isoDuration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  
  if (!matches) return 0;
  
  const hours = parseInt(matches[1]) || 0;
  const minutes = parseInt(matches[2]) || 0;
  const seconds = parseInt(matches[3]) || 0;
  
  return hours * 3600 + minutes * 60 + seconds;
}

/**
 * 秒数をHH:MM:SS形式に変換
 * @param {number} seconds - 秒数
 * @returns {string} HH:MM:SS形式の文字列
 */
function formatDuration(seconds) {
  if (!seconds || seconds === 0) return '0:00';
  
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  
  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  } else {
    return `${minutes}:${String(secs).padStart(2, '0')}`;
  }
}

/**
 * 動画情報データを整形
 * @param {Object} video - YouTube APIの動画オブジェクト
 * @param {string} channelName - チャンネル名
 * @param {string} channelId - チャンネルID
 * @returns {Array} スプレッドシート用の1行データ配列
 */
function formatVideoData(video, channelName, channelId) {
  const now = new Date();
  const snippet = video.snippet;
  const statistics = video.statistics;
  const contentDetails = video.contentDetails;
  
  // 再生時間を変換
  const durationSeconds = parseDuration(contentDetails.duration);
  const durationFormatted = formatDuration(durationSeconds);
  
  // タグを結合（配列をカンマ区切り文字列に）
  const tags = snippet.tags ? snippet.tags.join(', ') : '';
  
  // 動画URLを生成
  const videoUrl = `https://www.youtube.com/watch?v=${video.id}`;
  
  // 公開日時を日付オブジェクトに変換
  const publishedAt = snippet.publishedAt ? new Date(snippet.publishedAt) : '';
  
  return [
    now,                                          // 取得日時
    channelName,                                  // チャンネル名
    channelId,                                    // チャンネルID
    video.id,                                     // 動画ID
    snippet.title || '',                          // 動画タイトル
    publishedAt,                                  // 公開日時
    parseInt(statistics.viewCount) || 0,         // 視聴回数
    parseInt(statistics.likeCount) || 0,         // 高評価数
    parseInt(statistics.commentCount) || 0,      // コメント数
    durationSeconds,                              // 再生時間（秒）
    durationFormatted,                            // 再生時間（表示）
    tags,                                         // タグ
    snippet.categoryId || '',                     // カテゴリID
    snippet.description || '',                    // 説明文
    snippet.thumbnails?.high?.url || '',         // サムネイルURL
    videoUrl                                      // 動画URL
  ];
}

/**
 * 動画情報をスプレッドシートに書き込み
 * @param {Array<Array>} videoDataArray - 動画データの2次元配列
 */
function writeVideoInfo(videoDataArray) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(SHEET_NAMES.VIDEO_INFO);
  
  if (!sheet) {
    throw new Error('「動画情報」シートが見つかりません。');
  }
  
  // 既存のデータをクリア（ヘッダー行を除く）
  const lastRow = sheet.getLastRow();
  if (lastRow > 1) {
    sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn()).clear();
  }
  
  // データが空の場合は終了
  if (videoDataArray.length === 0) {
    Logger.log('書き込む動画データがありません。');
    return;
  }
  
  // データを書き込み
  const range = sheet.getRange(2, 1, videoDataArray.length, videoDataArray[0].length);
  range.setValues(videoDataArray);
  
  // 数値フォーマットを適用
  sheet.getRange(2, 7, videoDataArray.length, 1).setNumberFormat('#,##0');   // 視聴回数
  sheet.getRange(2, 8, videoDataArray.length, 1).setNumberFormat('#,##0');   // 高評価数
  sheet.getRange(2, 9, videoDataArray.length, 1).setNumberFormat('#,##0');   // コメント数
  sheet.getRange(2, 10, videoDataArray.length, 1).setNumberFormat('#,##0');  // 再生時間（秒）
  
  // 日時フォーマットを適用
  sheet.getRange(2, 1, videoDataArray.length, 1).setNumberFormat('yyyy-mm-dd hh:mm:ss');  // 取得日時
  sheet.getRange(2, 6, videoDataArray.length, 1).setNumberFormat('yyyy-mm-dd hh:mm:ss');  // 公開日時
  
  Logger.log(`${videoDataArray.length}件の動画情報を書き込みました。`);
}

// ============================================================
// メイン処理 - 動画情報取得
// ============================================================

/**
 * 1チャンネルの動画情報を取得
 * @param {string} channelId - チャンネルID
 * @param {string} channelName - チャンネル名
 * @param {number} maxVideos - 取得する最大動画数
 * @returns {Array<Array>} 動画データの2次元配列
 */
function fetchVideosForChannel(channelId, channelName, maxVideos) {
  try {
    // アップロードプレイリストIDを取得
    const uploadsPlaylistId = getUploadsPlaylistId(channelId);
    
    if (!uploadsPlaylistId) {
      Logger.log(`プレイリストIDが取得できません: ${channelName}`);
      return [];
    }
    
    // 動画IDリストを取得
    const videoIds = getVideoIdsFromPlaylist(uploadsPlaylistId, maxVideos);
    
    if (videoIds.length === 0) {
      Logger.log(`動画が見つかりません: ${channelName}`);
      return [];
    }
    
    // 動画の詳細情報を取得
    const videos = getVideosInfo(videoIds);
    
    // データを整形
    const videoDataArray = [];
    for (const video of videos) {
      const formattedData = formatVideoData(video, channelName, channelId);
      videoDataArray.push(formattedData);
    }
    
    return videoDataArray;
    
  } catch (error) {
    Logger.log(`チャンネルの動画取得エラー (${channelName}): ${error.toString()}`);
    return [];
  }
}

/**
 * 全チャンネルの動画情報を取得してスプレッドシートに書き込む
 * メニューから実行される主要な関数
 */
function fetchAllVideosInfo() {
  const startTime = new Date();
  
  try {
    showProgress('動画情報の取得を開始します...');
    
    // シートの存在確認
    if (!checkAllSheetsExist()) {
      throw new Error('必要なシートが揃っていません。セットアップを実行してください。');
    }
    
    // 設定を取得
    const maxVideos = getMaxVideos();
    
    // 有効なチャンネルリストを取得
    const channels = getActiveChannelIds();
    showProgress(`${channels.length}件のチャンネルから動画を取得します...`);
    
    const allVideoData = [];
    let totalVideos = 0;
    let successChannels = 0;
    let errorChannels = 0;
    
    // 各チャンネルの動画情報を取得
    for (let i = 0; i < channels.length; i++) {
      const channel = channels[i];
      showProgress(`[${i + 1}/${channels.length}] ${channel.memo || channel.id} の動画を取得中...`);
      
      // まずチャンネル情報を取得してチャンネル名を取得
      const channelInfo = getChannelInfo(channel.id);
      const channelName = channelInfo ? channelInfo.snippet.title : channel.memo;
      
      // 動画情報を取得
      const videoData = fetchVideosForChannel(channel.id, channelName, maxVideos);
      
      if (videoData.length > 0) {
        allVideoData.push(...videoData);
        totalVideos += videoData.length;
        successChannels++;
        Logger.log(`${channelName}: ${videoData.length}件の動画を取得`);
      } else {
        errorChannels++;
        Logger.log(`${channelName}: 動画取得失敗または動画なし`);
      }
      
      // API制限を避けるため、少し待機
      Utilities.sleep(500);
    }
    
    // データを書き込み
    if (allVideoData.length > 0) {
      showProgress('データを書き込んでいます...');
      writeVideoInfo(allVideoData);
    }
    
    // 完了メッセージ
    const endTime = new Date();
    const duration = ((endTime - startTime) / 1000).toFixed(1);
    
    const message = `✅ 動画情報取得完了\n\n` +
                    `処理チャンネル: ${successChannels}/${channels.length}件\n` +
                    `取得動画数: ${totalVideos}件\n` +
                    `所要時間: ${duration}秒`;
    
    SpreadsheetApp.getUi().alert('完了', message, SpreadsheetApp.getUi().ButtonSet.OK);
    Logger.log(message);
    
  } catch (error) {
    const errorMessage = `❌ エラーが発生しました\n\n${error.message}`;
    SpreadsheetApp.getUi().alert('エラー', errorMessage, SpreadsheetApp.getUi().ButtonSet.OK);
    Logger.log('エラー: ' + error.toString());
    throw error;
  }
}

// ============================================================
// メニュー実行用ラッパー関数
// ============================================================

/**
 * メニューから「チャンネル情報を取得」を実行
 */
function menuFetchChannelInfo() {
  try {
    fetchAllChannelInfo();
  } catch (error) {
    // エラーは fetchAllChannelInfo 内で処理済み
    Logger.log('メニュー実行エラー (チャンネル情報): ' + error.toString());
  }
}

/**
 * メニューから「動画情報を取得」を実行
 */
function menuFetchVideoInfo() {
  try {
    fetchAllVideosInfo();
  } catch (error) {
    // エラーは fetchAllVideosInfo 内で処理済み
    Logger.log('メニュー実行エラー (動画情報): ' + error.toString());
  }
}

/**
 * メニューから「すべて実行」を実行
 * チャンネル情報と動画情報を連続して取得
 */
function menuFetchAll() {
  const startTime = new Date();
  
  try {
    showProgress('すべてのデータ取得を開始します...');
    
    // チャンネル情報を取得
    showProgress('ステップ 1/2: チャンネル情報を取得中...');
    fetchAllChannelInfo();
    
    // 少し待機
    Utilities.sleep(1000);
    
    // 動画情報を取得
    showProgress('ステップ 2/2: 動画情報を取得中...');
    fetchAllVideosInfo();
    
    // 完了メッセージ
    const endTime = new Date();
    const duration = ((endTime - startTime) / 1000).toFixed(1);
    
    const message = `✅ すべてのデータ取得完了\n\n` +
                    `チャンネル情報と動画情報を取得しました。\n` +
                    `総所要時間: ${duration}秒`;
    
    SpreadsheetApp.getUi().alert('完了', message, SpreadsheetApp.getUi().ButtonSet.OK);
    Logger.log(message);
    
  } catch (error) {
    const errorMessage = `❌ データ取得中にエラーが発生しました\n\n${error.message}`;
    SpreadsheetApp.getUi().alert('エラー', errorMessage, SpreadsheetApp.getUi().ButtonSet.OK);
    Logger.log('すべて実行エラー: ' + error.toString());
  }
}

/**
 * メニューから「データをクリア」を実行
 * 確認ダイアログを表示してから実行
 */
function menuClearData() {
  const ui = SpreadsheetApp.getUi();
  
  // 確認ダイアログを表示
  const response = ui.alert(
    '確認',
    '「チャンネル情報」と「動画情報」のデータをすべてクリアします。\n\nよろしいですか？',
    ui.ButtonSet.YES_NO
  );
  
  // ユーザーが「はい」を選択した場合のみ実行
  if (response === ui.Button.YES) {
    try {
      clearAllData();
      
      const message = '✅ データクリア完了\n\nチャンネル情報と動画情報をクリアしました。';
      ui.alert('完了', message, ui.ButtonSet.OK);
      Logger.log('データクリア完了');
      
    } catch (error) {
      const errorMessage = `❌ データクリア中にエラーが発生しました\n\n${error.message}`;
      ui.alert('エラー', errorMessage, ui.ButtonSet.OK);
      Logger.log('データクリアエラー: ' + error.toString());
    }
  } else {
    showProgress('データクリアをキャンセルしました');
    Logger.log('データクリアがキャンセルされました');
  }
}

/**
 * チャンネル情報と動画情報のデータをクリア
 */
function clearAllData() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  
  // チャンネル情報シートをクリア
  const channelSheet = ss.getSheetByName(SHEET_NAMES.CHANNEL_INFO);
  if (channelSheet) {
    const lastRow = channelSheet.getLastRow();
    if (lastRow > 1) {
      channelSheet.getRange(2, 1, lastRow - 1, channelSheet.getLastColumn()).clear();
      Logger.log('チャンネル情報シートをクリアしました');
    }
  }
  
  // 動画情報シートをクリア
  const videoSheet = ss.getSheetByName(SHEET_NAMES.VIDEO_INFO);
  if (videoSheet) {
    const lastRow = videoSheet.getLastRow();
    if (lastRow > 1) {
      videoSheet.getRange(2, 1, lastRow - 1, videoSheet.getLastColumn()).clear();
      Logger.log('動画情報シートをクリアしました');
    }
  }
  
  showProgress('データをクリアしました');
}

// ============================================================
// デバッグ用関数
// ============================================================

/**
 * デバッグ: YouTube APIの動作確認
 * 1つのチャンネル情報を取得してログに出力
 */
function debugTestAPI() {
  try {
    Logger.log('=== YouTube API 動作確認開始 ===');
    
    // テスト用チャンネルID（MrBeast）
    const testChannelId = 'UCX6OQ3DkcsbYNE6H8uQQuVA';
    Logger.log('テストチャンネルID: ' + testChannelId);
    
    // APIサービスが利用可能か確認
    if (typeof YouTube === 'undefined') {
      Logger.log('❌ エラー: YouTube Data APIサービスが追加されていません');
      SpreadsheetApp.getUi().alert(
        'エラー',
        'YouTube Data API v3サービスが追加されていません。\n\n' +
        'Apps Scriptエディタの左側「サービス」から追加してください。',
        SpreadsheetApp.getUi().ButtonSet.OK
      );
      return;
    }
    
    Logger.log('✅ YouTube Data APIサービスが利用可能です');
    
    // チャンネル情報を取得
    Logger.log('チャンネル情報を取得中...');
    const response = YouTube.Channels.list('snippet,statistics', {
      id: testChannelId
    });
    
    if (!response.items || response.items.length === 0) {
      Logger.log('❌ チャンネルが見つかりませんでした');
      return;
    }
    
    const channel = response.items[0];
    Logger.log('✅ チャンネル情報取得成功！');
    Logger.log('チャンネル名: ' + channel.snippet.title);
    Logger.log('登録者数: ' + channel.statistics.subscriberCount);
    Logger.log('総視聴回数: ' + channel.statistics.viewCount);
    Logger.log('動画数: ' + channel.statistics.videoCount);
    
    // チャンネルリストシートの確認
    Logger.log('\n=== チャンネルリストシートの確認 ===');
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(SHEET_NAMES.CHANNEL_LIST);
    
    if (!sheet) {
      Logger.log('❌ チャンネルリストシートが見つかりません');
      return;
    }
    
    Logger.log('✅ チャンネルリストシートが存在します');
    
    const lastRow = sheet.getLastRow();
    Logger.log('最終行: ' + lastRow);
    
    if (lastRow < 2) {
      Logger.log('❌ チャンネルリストにデータがありません');
      return;
    }
    
    const data = sheet.getRange(2, 1, lastRow - 1, 3).getValues();
    Logger.log('データ行数: ' + data.length);
    
    let activeCount = 0;
    for (let i = 0; i < data.length; i++) {
      const channelId = data[i][0] ? data[i][0].toString().trim() : '';
      const memo = data[i][1] ? data[i][1].toString() : '';
      const isActive = data[i][2] === true;
      
      Logger.log(`行${i+2}: ID="${channelId}", メモ="${memo}", 有効=${isActive}`);
      
      if (channelId && isActive) {
        activeCount++;
      }
    }
    
    Logger.log('\n有効なチャンネル数: ' + activeCount);
    
    if (activeCount === 0) {
      Logger.log('❌ 有効なチャンネルが見つかりません');
      Logger.log('「有効」列（C列）にチェックを入れてください');
    }
    
    Logger.log('\n=== 動作確認完了 ===');
    
    SpreadsheetApp.getUi().alert(
      'デバッグ完了',
      'ログを確認してください。\n\n' +
      '表示 → ログ（または実行数）から詳細を確認できます。',
      SpreadsheetApp.getUi().ButtonSet.OK
    );
    
  } catch (error) {
    Logger.log('❌ エラー発生: ' + error.toString());
    Logger.log('エラー詳細: ' + error.message);
    Logger.log('スタックトレース: ' + error.stack);
    
    SpreadsheetApp.getUi().alert(
      'エラー',
      'エラーが発生しました:\n\n' + error.message + '\n\n' +
      'ログで詳細を確認してください。',
      SpreadsheetApp.getUi().ButtonSet.OK
    );
  }
}
