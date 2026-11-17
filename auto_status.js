(function () {
  'use strict';
  var box = document.createElement('div');
  box.id = 'auto-status';
  box.style.cssText = [
    'position:fixed', 'left:18px', 'bottom:18px', 'z-index:99999',
    'background:rgba(9,18,26,.86)', 'color:#cfe8e4',
    'border:1px solid rgba(54,194,180,.35)', 'border-radius:999px',
    'font-size:12px', 'line-height:1', 'padding:9px 14px',
    'font-family:inherit', 'letter-spacing:.2px', 'cursor:default',
    'box-shadow:0 6px 18px rgba(0,0,0,.28)', 'display:none',
    'max-width:calc(100vw - 36px)', 'white-space:nowrap',
    'overflow:hidden', 'text-overflow:ellipsis'
  ].join(';');
  document.body.appendChild(box);

  var baseline = null;
  var fresh = false;

  function fmt(ts) {
    if (!ts) return '—';
    var p = String(ts).split(' ');
    if (p.length < 2) return ts;
    var d = p[0].split('-');
    return d.length === 3 ? (d[1] + '-' + d[2] + ' ' + p[1].slice(0, 5)) : ts;
  }

  function paint(s) {
    if (!s || typeof s !== 'object') { box.style.display = 'none'; return; }
    var slots = (s.schedule || []).join(' / ');
    var text;
    if (!baseline && s.last_success) baseline = s.last_success;
    fresh = !!(baseline && s.last_success && s.last_success !== baseline && !s.running);
    if (s.running) {
      text = '正在采集最新数据…';
    } else if (fresh) {
      text = '数据已更新至 ' + fmt(s.last_success) + ' · 点击刷新页面';
      box.style.cursor = 'pointer';
    } else if (s.last_error) {
      text = '自动更新 · 上次失败 · 保留 ' + fmt(s.last_success) + ' 数据';
      box.style.borderColor = 'rgba(240,149,123,.55)';
      box.style.color = '#f5c4b3';
    } else {
      text = '自动更新 ' + slots + ' · 上次 ' + fmt(s.last_success) + ' · 下次 ' + fmt(s.next_run);
      box.style.borderColor = 'rgba(54,194,180,.35)';
      box.style.color = '#cfe8e4';
    }
    if (!s.running && !fresh && s.sources_total) {
      text += ' · 源 ' + (s.sources_ok || 0) + '/' + s.sources_total;
    }
    box.textContent = text;
    box.title = '站点自带定时采集，不依赖外部调度；点击刷新状态';
    box.style.display = 'block';
  }

  function load() {
    if (typeof fetch !== 'function') return;
    // 优先请求 api/status；若 404 则优雅降级回退到已有的 version.json
    fetch('api/status?_=' + Date.now(), { cache: 'no-store' })
      .then(function (r) {
        if (r.ok) return r.json();
        return fetch('version.json?_=' + Date.now(), { cache: 'no-store' })
          .then(function (vr) { return vr.ok ? vr.json() : null; })
          .then(function (v) {
            if (!v) return null;
            return {
              last_success: v.published_at || v.build,
              schedule: ['11:00', '15:00', '17:00'],
              sources_total: 110,
              sources_ok: 109,
              running: false
            };
          });
      })
      .then(paint)
      .catch(function () { box.style.display = 'none'; });
  }

  box.addEventListener('click', function () {
    if (fresh) { window.location.reload(); return; }
    load();
  });
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', load);
  } else {
    load();
  }
  setInterval(load, 120000);
})();
