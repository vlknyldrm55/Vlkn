#!/bin/bash
# =====================================================
#  M3U/M3U8 Proxy Otomatik Kurulum Scripti
# =====================================================

APP_NAME="m3u8-proxy"
PORT="7860"

echo "🚀 M3U8 Proxy kurulumu başlatılıyor..."

echo "📦 Docker imajı oluşturuluyor..."
docker build -t $APP_NAME .

echo "🧹 Eski konteyner varsa siliniyor..."
docker rm -f $APP_NAME >/dev/null 2>&1 || true

echo "🚀 Yeni konteyner başlatılıyor..."
docker run -d -p ${PORT}:${PORT} --name $APP_NAME $APP_NAME

echo "✅ Kurulum tamamlandı!"
echo "🌐 Uygulamayı test etmek için:"
echo "👉 http://localhost:${PORT}/"
