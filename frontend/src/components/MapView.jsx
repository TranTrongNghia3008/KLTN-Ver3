import { useEffect, useRef } from "react";
import { fetchLocationInformations } from "./services/qnaService";
import { BiQuestionMark } from "react-icons/bi";
import { renderToStaticMarkup } from "react-dom/server";

export default function MapView({ conversationId, onSendMessageFromLocation, setLocations }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const infoWindowRef = useRef(null);
  const markersRef = useRef([]);
  const iconHTML = renderToStaticMarkup(<BiQuestionMark />);

  const clearMarkers = () => {
    markersRef.current.forEach((marker) => marker.setMap(null));
    markersRef.current = [];
  };

  // ✅ Khởi tạo bản đồ ngay từ đầu
  useEffect(() => {
    if (!window.google || !mapRef.current || mapInstanceRef.current) return;

    mapInstanceRef.current = new window.google.maps.Map(mapRef.current, {
      zoom: 2,
      center: { lat: 0, lng: 0 },
    });
  }, []);

  // ✅ Hiển thị địa điểm khi có conversationId
  useEffect(() => {
    if (!conversationId) return;

    fetchLocationInformations(conversationId)
      .then((res) => {
        const locations = res || [];
        setLocations(locations);
        const map = mapInstanceRef.current;
        if (!map) return;

        clearMarkers();

        const icons = {
          positive: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
          negative: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
          neutral: 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
        };

        locations.forEach((loc) => {
          const marker = new window.google.maps.Marker({
            position: { lat: loc.lat, lng: loc.lon },
            map,
            icon: icons[loc.sentiment] || icons["neutral"],
            title: `${loc.administrative_area}, ${loc.country}`,
          });

          let content = `<b>${loc.administrative_area}, ${loc.country}</b><br/>`;
          loc.links.forEach((link, i) => {
            const summary = loc.summaries?.[i] || "No summary";
            content += `
              <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                <a href="${link}" target="_blank" rel="noopener noreferrer" style="flex: 1;">${summary}</a>
                <a href="#"
                  class="qa-trigger"
                  data-summary="${encodeURIComponent(summary)}"
                  data-link="${encodeURIComponent(link)}"
                  title="Questions and answers about this information"
                  style="display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; border-radius: 50%; background-color: #eee; text-decoration: none; cursor: pointer;"
                >
                  ${iconHTML}
                </a>
              </div>
            `;
          });

          const infoWindow = new window.google.maps.InfoWindow({ content });

          marker.addListener("click", () => {
            if (infoWindowRef.current) infoWindowRef.current.close();
            infoWindow.open(map, marker);
            infoWindowRef.current = infoWindow;

            window.google.maps.event.addListenerOnce(infoWindow, 'domready', () => {
              const buttons = document.querySelectorAll('.qa-trigger');
              buttons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                  e.preventDefault();
                  const summary = decodeURIComponent(e.currentTarget.getAttribute('data-summary'));
                  const link = decodeURIComponent(e.currentTarget.getAttribute('data-link'));
                  onSendMessageFromLocation && onSendMessageFromLocation(summary, link);
                });
              });
            });
          });

          markersRef.current.push(marker);
        });
      })
      .catch((err) => console.error("Lỗi lấy địa điểm:", err));
  }, [conversationId]);

  return (
    <div className="h-full w-full">
      <div ref={mapRef} className="w-full h-full" />
    </div>
  );
}
