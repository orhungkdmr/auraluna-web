document.addEventListener('DOMContentLoaded', function() {

    // --- NETWORK TARZI MEGA MENÜ HOVER ETKİLEŞİMİ ---
    const networkMenus = document.querySelectorAll('.network-style-menu');

    networkMenus.forEach(menu => {
        const intermediateItems = menu.querySelectorAll('.intermediate-category-item');
        const finalSubmenus = menu.querySelectorAll('.final-category-submenu');

        intermediateItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                intermediateItems.forEach(i => i.classList.remove('active'));
                this.classList.add('active');
                finalSubmenus.forEach(submenu => submenu.classList.remove('active'));
                const targetId = this.dataset.target;
                if (targetId) {
                    const targetSubmenu = menu.querySelector(targetId);
                    if (targetSubmenu) {
                        targetSubmenu.classList.add('active');
                    }
                }
            });
        });

        const megaMenuContent = menu.querySelector('.mega-menu-content');
        if (megaMenuContent) {
            megaMenuContent.addEventListener('mouseleave', function() {
                intermediateItems.forEach(i => i.classList.remove('active'));
                finalSubmenus.forEach(submenu => submenu.classList.remove('active'));
            });
        }
    });
    // --- NETWORK MENÜ KODU SONU ---


    // --- DUYURU BANDI SWIPER BAŞLATMA ---
    if (document.querySelector('.announcement-swiper')) {
        const announcementSlides = document.querySelectorAll('.announcement-swiper .swiper-slide');
        const allowLoop = announcementSlides.length > 1;

        new Swiper('.announcement-swiper', {
            direction: 'vertical',
            loop: allowLoop,
            autoplay: allowLoop ? {
                delay: 4000,
                disableOnInteraction: false,
            } : false,
            effect: 'slide',
        });
    }
    // --- DUYURU BANDI KODU SONU ---


// --- HEADER ARKA PLANINI GÜNCELLEME FONKSİYONU (GÜNCELLENDİ) ---
const headerElement = document.querySelector('.site-header');
const heroSwiperElement = document.querySelector('.hero-swiper'); // Swiper elementini seç

function updateHeaderBackground(swiperInstance) {
    if (!swiperInstance || !headerElement || !swiperInstance.slides || swiperInstance.slides.length === 0) {
         if(headerElement) headerElement.style.setProperty('--header-bg-image', 'none');
        return;
    }
    try {
        
        // ============================================
        // === GÜNCELLEME BURADA: realIndex -> activeIndex ===
        // ============================================
        
        // Bize 'gerçek' slayt indeksi değil, DOM'daki 'aktif' slayt elementi lazım.
        const activeSlide = swiperInstance.slides[swiperInstance.activeIndex];
        
        
        if (activeSlide) {
            // HTML'de (<div style="--slide-bg-image: url(...)">) tanımlanan
            // CSS değişkenini doğrudan okuyalım. Bu en güvenilir yöntem.
            const imageUrl = activeSlide.style.getPropertyValue('--slide-bg-image').trim();
            
            if (imageUrl) {
                headerElement.style.setProperty('--header-bg-image', imageUrl);
            } else {
                 // Değişken bulunamazsa, güvenlik için temizle
                 headerElement.style.setProperty('--header-bg-image', 'none');
            }
        } else {
            headerElement.style.setProperty('--header-bg-image', 'none');
        }
    } catch (e) {
         console.error("Header background update error:", e);
         if(headerElement) headerElement.style.setProperty('--header-bg-image', 'none');
    }
}
// --- HEADER ARKA PLAN KODU SONU ---

    // --- KAYDIRINCA DEĞİŞEN NAVBAR MANTIĞI ---
    const scrollNavbar = document.querySelector('.site-header'); // .navbar.fixed-top yerine .site-header seçildi
    if (scrollNavbar) { // Değişken adı da güncellendi
        window.addEventListener('scroll', function() {
            // 'scrolled' sınıfı eklenecek/kaldırılacak, bu sınıfın CSS'te tanımlanması gerekebilir
            if (window.scrollY > 50) {
                scrollNavbar.classList.add('scrolled');
            } else {
                scrollNavbar.classList.remove('scrolled');
            }
        });
    }

    // --- TOAST BİLDİRİM FONKSİYONU ---
    function showToast(message, type = 'success') {
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) return;
        const toastId = 'toast-' + Date.now();
        const toastClass = type === 'danger' ? 'text-bg-danger' : (type === 'warning' ? 'text-bg-warning' : 'text-bg-success');

        const toastHTML = `
            <div class="toast align-items-center ${toastClass} border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="4000" id="${toastId}">
              <div class="d-flex">
                <div class="toast-body">
                  ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
              </div>
            </div>`;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const newToastEl = document.getElementById(toastId);
        const newToast = new bootstrap.Toast(newToastEl);
        newToast.show();
        newToastEl.addEventListener('hidden.bs.toast', () => newToastEl.remove());
    }


    // --- CSRF TOKEN YARDIMCI FONKSİYONU ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // --- AJAX FAVORİ MANTIĞI ---
    document.body.addEventListener('click', function(event) {
        const favouriteLink = event.target.closest('.js-toggle-favourite');
        if (favouriteLink) {
            event.preventDefault();
            const url = favouriteLink.href;
            const heartIcon = favouriteLink.querySelector('i');
            fetch(url, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCookie('csrftoken') },
            })
            .then(response => {
                 if (!response.ok) { throw new Error('Network response was not ok ' + response.statusText); }
                 return response.json();
            })
            .then(data => {
                if (data.status === 'ok') {
                    showToast(data.message);
                    if(heartIcon){ // İkon varsa sınıfı değiştir
                        if (data.is_favourited) { heartIcon.classList.remove('bi-heart'); heartIcon.classList.add('bi-heart-fill'); }
                        else { heartIcon.classList.remove('bi-heart-fill'); heartIcon.classList.add('bi-heart'); }
                    }
                } else {
                     showToast(data.message || 'Bir hata oluştu.', 'danger');
                }
            })
            .catch(error => {
                console.error('Favori işlemi sırasında hata:', error);
                showToast('İşlem sırasında bir hata oluştu. Lütfen tekrar deneyin.', 'danger');
            });
        }
    });

    // --- AJAX SEPET İŞLEMLERİ ---
    document.body.addEventListener('submit', function(event) {
        const cartForm = event.target.closest('.js-ajax-cart-form');
        if (cartForm) {
            event.preventDefault();
            const url = cartForm.action;
            const formData = new FormData(cartForm);
            fetch(url, {
                method: 'POST', body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCookie('csrftoken') },
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errData => { throw errData; });
                }
                return response.json();
             })
            .then(data => {
                if (data.status === 'ok') {
                    showToast(data.message);
                    const cartCounter = document.getElementById('cart-counter');
                    if (cartCounter) {
                        cartCounter.textContent = data.cart_total_items;
                        cartCounter.style.display = data.cart_total_items > 0 ? 'inline-block' : 'none';
                    }
                } else if (data.status === 'reload') {
                    showToast(data.message);
                    setTimeout(() => window.location.reload(), 1000);
                }
            })
            .catch(errorData => {
                console.error('Sepet işlemi sırasında hata:', errorData);
                const message = errorData.message || 'İşlem sırasında bir hata oluştu. Stok yetersiz olabilir veya geçersiz bir miktar girdiniz.';
                showToast(message, 'danger');
            });
        }
    });

    // --- ANA SAYFA KARUSELLERİ ---
    if (heroSwiperElement) { // Swiper elementini kontrol et
        const heroSwiperInstance = new Swiper('.hero-swiper', { // instance'ı değişkene ata
            loop: true,
            autoplay: { delay: 5000, disableOnInteraction: false },
            pagination: { el: '.swiper-pagination', clickable: true },
            effect: 'fade',
            fadeEffect: { crossFade: true },
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            
            on: { 
                // Swiper tam yüklendiğinde bir kez çalıştır
                afterInit: function (swiper) {
                    updateHeaderBackground(swiper); 
                },
                
                // Slayt geçişi TAMAMLANDIĞINDA çalıştır (Normal geçişler için)
                slideChangeTransitionEnd: function (swiper) {
                    updateHeaderBackground(swiper);
                },

                // YENİ EKLENDİ (DÖNGÜ HATASI İÇİN):
                // "Gerçek" slayt indeksi değiştiğinde (loop anı dahil) 
                // animasyon bitmeden hemen tetiklenir.
                realIndexChange: function (swiper) {
                    updateHeaderBackground(swiper);
                }
            }
            
        });
    }

    if (document.querySelector('.product-swiper')) {
        new Swiper('.product-swiper', {
            slidesPerView: 1,
            spaceBetween: 10,
            breakpoints: {
                 576: { slidesPerView: 2, spaceBetween: 20 },
                 768: { slidesPerView: 3, spaceBetween: 30 },
                 992: { slidesPerView: 4, spaceBetween: 30 }
            },
            navigation: { nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' }
        });
    }

    // --- HIZLI BAKIŞ (QUICK VIEW) MODAL MANTIĞI ---
    const quickViewModalEl = document.getElementById('quickViewModal');
    if (quickViewModalEl) {
        const modalBody = quickViewModalEl.querySelector('.modal-body');
        quickViewModalEl.addEventListener('show.bs.modal', function(event) {
            const button = event.relatedTarget;
            if (!button) return;
            const productSlug = button.dataset.slug;
            if (!productSlug) return;

            const url = `/products/quick-view/${productSlug}/`;
            modalBody.innerHTML = '<div class="d-flex justify-content-center align-items-center" style="min-height: 300px;"><div class="spinner-border" role="status"><span class="visually-hidden">Yükleniyor...</span></div></div>';
            fetch(url)
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                 })
                .then(data => {
                    modalBody.innerHTML = `
                        <div class="row">
                            <div class="col-md-6">
                                <img src="${data.main_image ? data.main_image : '/static/images/placeholder.png'}" class="img-fluid rounded">
                            </div>
                            <div class="col-md-6">
                                <h3>${data.name || 'Ürün Adı Yok'}</h3>
                                <p class="text-muted">${data.category || ''}</p>
                                <p>${data.description ? data.description.substring(0, 150) + '...' : ''}</p>
                                <hr>
                                <a href="/products/p/${productSlug}/" class="btn btn-primary">Tüm Detayları Gör</a>
                            </div>
                        </div>`;
                })
                .catch(error => {
                    modalBody.innerHTML = '<p class="text-danger">Ürün bilgileri yüklenirken bir hata oluştu.</p>';
                    console.error('Hızlı Bakış Hatası:', error);
                 });
        });
    }

    // ==================================================
    // === GÜNCELLENEN ÜRÜN DETAY SAYFASI MANTIĞI ===
    // (Dinamik Renk Kodları Kullanır)
    // ==================================================
    const variantsDataEl = document.getElementById('variants-data');
    if (variantsDataEl) {
        try {
            const variantsData = JSON.parse(variantsDataEl.textContent); const variants = variantsData;
            const mainImage = document.getElementById('main-product-image'); const thumbnails = document.querySelectorAll('.thumbnail-img');
            const colorSelector = document.getElementById('color-selector'); const sizeSelector = document.getElementById('size-selector');
            const priceDisplay = document.getElementById('product-price'); const stockDisplay = document.getElementById('product-stock');
            const addToCartBtn = document.getElementById('add-to-cart-btn'); const addToCartForm = document.getElementById('add-to-cart-form');
            const quantityInput = document.getElementById('quantity-input'); const quantityMinusBtn = document.getElementById('quantity-minus'); const quantityPlusBtn = document.getElementById('quantity-plus');
            let selectedColor = null, selectedSize = null, currentVariant = null;

            thumbnails.forEach(thumb => {
                thumb.addEventListener('click', function() {
                    if (mainImage) mainImage.src = this.src;
                    thumbnails.forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                });
            });

            if (colorSelector && variants && variants.length > 0) {
                
                // YENİ: Benzersiz renkleri (nesne olarak) al
                const uniqueColorObjects = [];
                const seenColorNames = new Set();
                variants.forEach(v => {
                    if (v.color && !seenColorNames.has(v.color)) {
                        uniqueColorObjects.push({ name: v.color, hex: v.hex_code });
                        seenColorNames.add(v.color);
                    }
                });
                 
                colorSelector.innerHTML = '';
                 
                // ARTIK GEREKLİ DEĞİL: const colorMap = { ... };

                // YENİ GÜNCELLENMİŞ DÖNGÜ: API'den gelen hex kodunu kullan
                uniqueColorObjects.forEach(colorObj => {
                    const colorDiv = document.createElement('div');
                    colorDiv.className = 'variant-swatch color-swatch';
                    colorDiv.dataset.color = colorObj.name; // data-color metin olarak kalmalı (örn: "Beyaz")
                    
                    // API'den gelen hex kodunu doğrudan kullan
                    colorDiv.style.backgroundColor = colorObj.hex || '#CCCCCC';
                    colorDiv.title = colorObj.name; // Fareyle üzerine gelince metni göster
                    
                    colorSelector.appendChild(colorDiv);
                });
                // --- GÜNCELLENMİŞ DÖNGÜ SONU ---

                 colorSelector.querySelectorAll('.color-swatch').forEach(swatch => {
                     swatch.addEventListener('click', function() {
                         selectedColor = this.dataset.color;
                         selectedSize = null;
                         colorSelector.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
                         this.classList.add('selected');
                         updateSizeOptions();
                         resetDisplayPartial();
                     });
                 });
            } else if (colorSelector) {
                 colorSelector.innerHTML = '<small class="text-muted">Renk seçeneği bulunmuyor.</small>';
            }

            function updateSizeOptions() {
                if (!sizeSelector || !variants) return;
                sizeSelector.innerHTML = '';
                if (!selectedColor) {
                    sizeSelector.innerHTML = '<small class="text-muted">Önce renk seçiniz.</small>';
                    return;
                }

                const availableVariants = variants.filter(v => v.color === selectedColor);
                if (availableVariants.length === 0) {
                     sizeSelector.innerHTML = '<small class="text-muted">Bu renk için beden bulunmuyor.</small>';
                     return;
                }

                availableVariants.forEach(variant => {
                    const sizeDiv = document.createElement('div');
                    sizeDiv.className = 'variant-swatch size-swatch';
                    sizeDiv.textContent = variant.size; // Artık v.size bir nesne değil, view'da 'name'ini aldık
                    sizeDiv.dataset.variantId = variant.id;
                    if (variant.stock <= 0) {
                        sizeDiv.classList.add('disabled');
                    }
                    sizeSelector.appendChild(sizeDiv);
                });

                sizeSelector.querySelectorAll('.size-swatch:not(.disabled)').forEach(swatch => {
                    swatch.addEventListener('click', function() {
                        selectedSize = this.textContent;
                        sizeSelector.querySelectorAll('.size-swatch').forEach(s => s.classList.remove('selected'));
                        this.classList.add('selected');
                        updateDisplay();
                    });
                });
            }

            if (quantityMinusBtn && quantityInput) {
                 quantityMinusBtn.addEventListener('click', () => {
                     let val = parseInt(quantityInput.value);
                     if (val > 1) {
                        quantityInput.value = val - 1;
                        updateQuantityButtons(); // Buton durumunu güncelle
                     }
                 });
            }
            if (quantityPlusBtn && quantityInput) {
                 quantityPlusBtn.addEventListener('click', () => {
                     let val = parseInt(quantityInput.value);
                     if (currentVariant && val < currentVariant.stock) {
                         quantityInput.value = val + 1;
                         updateQuantityButtons(); // Buton durumunu güncelle
                     }
                 });
            }

            // Miktar butonlarının aktif/pasif durumunu günceller
            function updateQuantityButtons() {
                if (!currentVariant || !quantityInput) return;
                let val = parseInt(quantityInput.value);
                if(quantityMinusBtn) quantityMinusBtn.disabled = val <= 1;
                if(quantityPlusBtn) quantityPlusBtn.disabled = val >= currentVariant.stock;
            }


            function resetDisplayFull() {
                 resetDisplayPartial();
                 if(colorSelector) colorSelector.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
                 selectedColor = null;
                 if(sizeSelector) sizeSelector.innerHTML = '<small class="text-muted">Önce renk seçiniz.</small>';
            }

            function resetDisplayPartial() {
                 if (priceDisplay) priceDisplay.textContent = 'Fiyat için seçim yapın';
                 if (stockDisplay) stockDisplay.textContent = 'Beden seçiniz'; // Beden seçiniz daha uygun
                 if (addToCartBtn) addToCartBtn.disabled = true;
                 if (quantityMinusBtn) quantityMinusBtn.disabled = true;
                 if (quantityPlusBtn) quantityPlusBtn.disabled = true;
                 if (quantityInput) {
                    quantityInput.value = 1;
                    quantityInput.max = 1;
                 }
                 currentVariant = null;
                 selectedSize = null;
                 if(sizeSelector) sizeSelector.querySelectorAll('.size-swatch').forEach(s => s.classList.remove('selected'));
                 // Renk seçiliyse bedenleri tekrar yükle ama seçimi sıfırla
                 if (selectedColor) updateSizeOptions();
            }

            function updateDisplay() {
                 if (selectedColor && selectedSize && variants) {
                     currentVariant = variants.find(v => v.color === selectedColor && v.size === selectedSize);
                     if (currentVariant) {
                         if (priceDisplay) priceDisplay.textContent = `${currentVariant.price} TL`;
                         if (quantityInput) quantityInput.max = currentVariant.stock;

                         if (currentVariant.stock > 0) {
                             if (stockDisplay) stockDisplay.textContent = `Stok: ${currentVariant.stock} adet`;
                             if (addToCartBtn) addToCartBtn.disabled = false;
                             if (quantityInput) quantityInput.value = Math.min(parseInt(quantityInput.value) || 1, currentVariant.stock);
                             updateQuantityButtons(); // Miktar butonlarını güncelle

                             if (addToCartForm) {
                                 const baseUrl = addToCartForm.dataset.baseAction;
                                 if (baseUrl) {
                                      addToCartForm.action = baseUrl.replace('0', currentVariant.id);
                                 }
                             }
                         } else {
                             if (stockDisplay) stockDisplay.textContent = 'Tükendi';
                             resetDisplayPartial();
                         }
                     } else {
                        resetDisplayPartial();
                     }
                 }
            }

            resetDisplayFull();

        } catch (e) {
            console.error("Varyasyon verisi işlenirken hata oluştu:", e);
            if(document.getElementById('product-price')) {
                document.getElementById('product-price').textContent = 'Seçenekler yüklenemedi.';
                document.getElementById('product-price').classList.add('text-danger');
            }
             if(document.getElementById('add-to-cart-btn')) {
                 document.getElementById('add-to-cart-btn').disabled = true;
            }
        }
    }


    // ========================================================
    // === YENİ EKLENEN KOD 1: RESİM DÖNGÜSÜ ===
    // ========================================================
    
    // --- ÜRÜN LİSTESİ HOVER RESİM DÖNGÜSÜ ---
    // product_list.html'deki ".product-image-container" sınıfını hedef alıyoruz
    const productHoverContainers = document.querySelectorAll('.product-list-item .product-image-container');

    productHoverContainers.forEach(container => {
        // Kartın içindeki ana resim etiketini bul
        const img = container.querySelector('.js-hover-cycle-image');
        
        // Gerekli nitelikler yoksa bu kartı atla
        if (!img || !img.dataset.mainImage || !img.dataset.gallery) {
            return;
        }

        const mainImage = img.dataset.mainImage;
        const galleryImages = img.dataset.gallery.split(',').filter(url => url.length > 0);

        // Eğer galeri boşsa (ana resim dışında resim yoksa) işlem yapma
        if (galleryImages.length === 0) {
            return;
        }

        // Ana resmi ve galeri resimlerini birleştir
        const allImages = [mainImage, ...galleryImages];
        
        let cycleInterval; // Zamanlayıcının (setInterval) kimliğini tutacak değişken
        let currentIndex = 0;

        // 1. Fare kartın üzerine geldiğinde (mouseenter)
        container.addEventListener('mouseenter', () => {
            // Döngüyü başlat
            cycleInterval = setInterval(() => {
                // Dizideki bir sonraki resme geç
                // (Mod alma (%) işlemi, dizinin sonuna gelince başa dönmeyi sağlar)
                currentIndex = (currentIndex + 1) % allImages.length;
                
                // Resmin src (kaynak) niteliğini yeni resim URL'si ile değiştir
                img.src = allImages[currentIndex];
                
            }, 800); // Her 800 milisaniyede (0.8 saniye) bir resmi değiştir
        });

        // 2. Fare kartın üzerinden çekildiğinde (mouseleave)
        container.addEventListener('mouseleave', () => {
            // Başlatılmış olan zamanlayıcıyı (döngüyü) durdur
            clearInterval(cycleInterval);
            
            // Resmi, orijinal ana resme geri döndür
            img.src = mainImage;
            
            // İndeksi sıfırla (bir sonraki hover için)
            currentIndex = 0;
        });
    });
    // --- ÜRÜN LİSTESİ HOVER RESİM DÖNGÜSÜ SONU ---


    // ========================================================
    // === YENİ EKLENEN KOD 2: HIZLI EKLE PANELİ ===
    // (Dinamik Renk Kodları Kullanır)
    // ========================================================

    // --- HIZLI EKLE (QUICK ADD) PANELİ MANTIĞI ---
    
    // ARTIK GEREKLİ DEĞİL: const quickAddColorMap = { ... };

    // Tüm ürün kartlarını seç
    const productCards = document.querySelectorAll('.product-list-item .product-card');

    productCards.forEach(card => {
        const quickAddContainer = card.querySelector('.quick-add-section');
        const slug = card.dataset.productSlug;
        let isLoaded = false; // Verinin API'den çekilip çekilmediğini kontrol eder

        // Fare kartın üzerine geldiğinde
        card.addEventListener('mouseenter', () => {
            // Eğer veri zaten yüklenmişse, tekrar yükleme
            if (isLoaded || !slug || !quickAddContainer) return;

            // API'yi çağır
            fetch(`/products/quick-view/${slug}/`)
                .then(response => {
                    if (!response.ok) throw new Error('Network response error');
                    return response.json();
                })
                .then(data => {
                    // API'den gelen veriyi (data.variants) kullanarak arayüzü oluştur
                    buildQuickAddUI(quickAddContainer, data.variants, data.add_to_cart_url_base);
                    isLoaded = true; // Yüklendi olarak işaretle
                })
                .catch(error => {
                    // Hata olursa spinner'ı kaldırıp hata mesajı göster
                    console.error('Quick Add Error:', error);
                    if(quickAddContainer) quickAddContainer.innerHTML = '<small class="text-danger p-2 d-block text-center">Yüklenemedi.</small>';
                });
        });
    });

    /**
     * API'den gelen varyant verisiyle Hızlı Ekle formunu oluşturur.
     */
    function buildQuickAddUI(container, variants, baseActionUrl) {
        if (!variants || variants.length === 0) {
            container.innerHTML = '<small class="text-muted p-2 d-block text-center">Seçenek yok.</small>';
            return;
        }

        // YENİ: Benzersiz renkleri (nesne olarak) al
        const uniqueColorObjects = [];
        const seenColorNames = new Set();
        variants.forEach(v => {
            if (v.color && !seenColorNames.has(v.color)) {
                uniqueColorObjects.push({ name: v.color, hex: v.hex_code });
                seenColorNames.add(v.color);
            }
        });
        
        // Formun HTML yapısını oluştur (GÜNCELLENDİ)
        container.innerHTML = `
            <form method="post" class="js-ajax-cart-form quick-add-form p-2" data-base-action="${baseActionUrl}">
                <div class="quick-view-variants-container">
                    
                    <div class="quick-view-colors">
                        ${uniqueColorObjects.map(colorObj => `
                            <div class="variant-swatch color-swatch" 
                                 data-color="${colorObj.name}" 
                                 title="${colorObj.name}"
                                 style="background-color: ${colorObj.hex || '#CCCCCC'};">
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="quick-view-sizes">
                        <small class="text-muted">Renk seçiniz</small>
                    </div>
                    
                </div>
                <input type="hidden" name="quantity" value="1">
                <button type="submit" class="btn btn-dark btn-sm w-100" disabled>Sepete Ekle</button>
            </form>
        `;

        // Bu yeni oluşturulan form için varyant seçme mantığını başlat
        initializeQuickAddLogic(container, variants);
    }

    /**
     * Dinamik olarak oluşturulan Hızlı Ekle formuna seçme mantığını ekler.
     */
    function initializeQuickAddLogic(container, variants) {
        const form = container.querySelector('form');
        const colorSwatches = container.querySelectorAll('.color-swatch');
        const sizeContainer = container.querySelector('.quick-view-sizes');
        const addToCartBtn = container.querySelector('button[type="submit"]');

        let selectedColor = null;
        let currentVariant = null;

        colorSwatches.forEach(swatch => {
            swatch.addEventListener('click', (e) => {
                e.stopPropagation(); // Olayın karttan yukarıya yayılmasını engelle
                selectedColor = swatch.dataset.color;
                
                // Diğerlerini sıfırla ve bunu seç
                colorSwatches.forEach(s => s.classList.remove('selected'));
                swatch.classList.add('selected');
                
                // Bedenleri güncelle
                updateSizeSwatches(sizeContainer, variants, selectedColor);
                
                // Formu sıfırla
                addToCartBtn.disabled = true;
                currentVariant = null;
            });
        });

        // Tıklama olayını beden konteynerına ekle (event delegation)
        sizeContainer.addEventListener('click', (e) => {
            e.stopPropagation();
            const target = e.target;
            
            // Tıklanan bir beden kutucuğu mu (ve stokta var mı)?
            if (target.classList.contains('size-swatch') && !target.classList.contains('disabled')) {
                // Diğerlerini sıfırla ve bunu seç
                sizeContainer.querySelectorAll('.size-swatch').forEach(s => s.classList.remove('selected'));
                target.classList.add('selected');

                // Seçili varyantı bul
                const variantId = target.dataset.variantId;
                currentVariant = variants.find(v => v.id == variantId);

                if (currentVariant) {
                    // Formun action URL'ini güncelle
                    const baseUrl = form.dataset.baseAction;
                    form.action = baseUrl.replace('0', currentVariant.id);
                    // Butonu aktif et
                    addToCartBtn.disabled = false;
                }
            }
        });
    }

    /**
     * Renk seçimine göre beden kutucuklarını günceller.
     */
    function updateSizeSwatches(sizeContainer, variants, selectedColor) {
        const availableVariants = variants.filter(v => v.color === selectedColor);
        
        if (availableVariants.length === 0) {
            sizeContainer.innerHTML = '<small class="text-danger">Seçenek yok.</small>';
            return;
        }

        sizeContainer.innerHTML = availableVariants.map(variant => `
            <div class="variant-swatch size-swatch ${variant.stock <= 0 ? 'disabled' : ''}"
                 data-variant-id="${variant.id}"
                 title="${variant.size}">
                 ${variant.size}
            </div>
        `).join('');
    }

    // --- HIZLI EKLE (QUICK ADD) PANELİ MANTIĞI SONU ---


}); // DOMContentLoaded sonu