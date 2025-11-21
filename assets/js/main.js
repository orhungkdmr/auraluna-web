document.addEventListener('DOMContentLoaded', function() {

    // ==================================================
    // 1. MENÜ VE ARAYÜZ (HEADER, SCROLL, TOAST)
    // ==================================================

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

    // --- DUYURU BANDI SWIPER ---
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

    // --- HEADER ARKA PLANINI GÜNCELLEME ---
    const headerElement = document.querySelector('.site-header');
    const heroSwiperElement = document.querySelector('.hero-swiper');

    function updateHeaderBackground(swiperInstance) {
        if (!swiperInstance || !headerElement || !swiperInstance.slides || swiperInstance.slides.length === 0) {
             if(headerElement) headerElement.style.setProperty('--header-bg-image', 'none');
            return;
        }
        try {
            const activeSlide = swiperInstance.slides[swiperInstance.activeIndex];
            if (activeSlide) {
                const imageUrl = activeSlide.style.getPropertyValue('--slide-bg-image').trim();
                if (imageUrl) {
                    headerElement.style.setProperty('--header-bg-image', imageUrl);
                } else {
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

    // --- KAYDIRINCA DEĞİŞEN NAVBAR (SCROLL) ---
    const scrollNavbar = document.querySelector('.site-header');
    if (scrollNavbar) {
        window.addEventListener('scroll', function() {
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

    // --- COOKIE YARDIMCISI ---
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

    // ==================================================
    // 2. SEPET VE FAVORİ İŞLEMLERİ (AJAX)
    // ==================================================

    // --- FAVORİYE EKLE/ÇIKAR ---
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
                    if(heartIcon){
                        if (data.is_favourited) { heartIcon.classList.remove('bi-heart'); heartIcon.classList.add('bi-heart-fill'); }
                        else { heartIcon.classList.remove('bi-heart-fill'); heartIcon.classList.add('bi-heart'); }
                    }
                } else {
                     showToast(data.message || 'Bir hata oluştu.', 'danger');
                }
            })
            .catch(error => {
                console.error('Favori hatası:', error);
                showToast('Bir hata oluştu.', 'danger');
            });
        }
    });

    // --- SEPETE EKLE (OFFCANVAS AÇILIR) ---
    document.body.addEventListener('submit', function(event) {
        const cartForm = event.target.closest('.js-ajax-cart-form');
        if (cartForm) {
            event.preventDefault();
            const url = cartForm.action;
            const formData = new FormData(cartForm);
            const submitBtn = cartForm.querySelector('button[type="submit"]');
            
            if(submitBtn) { 
                var originalText = submitBtn.innerText;
                submitBtn.disabled = true; 
                submitBtn.innerText = "Ekleniyor...";
            }

            fetch(url, {
                method: 'POST', body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCookie('csrftoken') },
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    showToast(data.message);
                    
                    // Sayacı güncelle
                    const cartCounter = document.getElementById('cart-counter');
                    if (cartCounter) {
                        cartCounter.textContent = data.cart_total_items;
                        cartCounter.style.display = data.cart_total_items > 0 ? 'inline-block' : 'none';
                    }

                    // Offcanvas içeriğini güncelle ve aç
                    const offcanvasBody = document.getElementById('offcanvas-cart-body');
                    if (offcanvasBody && data.cart_html) {
                        offcanvasBody.innerHTML = data.cart_html;
                        const offcanvasElement = document.getElementById('offcanvasCart');
                        const bsOffcanvas = new bootstrap.Offcanvas(offcanvasElement);
                        bsOffcanvas.show();
                    }

                } else {
                    showToast(data.message || 'Hata oluştu.', 'danger');
                }
            })
            .catch(error => {
                console.error('Sepet hatası:', error);
                showToast('Bir hata oluştu.', 'danger');
            })
            .finally(() => {
                if(submitBtn) { 
                    submitBtn.disabled = false; 
                    submitBtn.innerText = originalText;
                }
            });
        }
    });

    // --- SEPETTEN SİL (MİNİ SEPET İÇİNDEN) ---
    document.body.addEventListener('submit', function(event) {
        const removeForm = event.target.closest('.js-offcanvas-remove-form');
        if (removeForm) {
            event.preventDefault();
            const url = removeForm.action;
            
            fetch(url, {
                method: 'POST',
                headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': getCookie('csrftoken') },
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    const cartCounter = document.getElementById('cart-counter');
                    if (cartCounter) {
                        cartCounter.textContent = data.cart_total_items;
                        cartCounter.style.display = data.cart_total_items > 0 ? 'inline-block' : 'none';
                    }

                    const offcanvasBody = document.getElementById('offcanvas-cart-body');
                    if (offcanvasBody && data.cart_html) {
                        offcanvasBody.innerHTML = data.cart_html;
                    }
                    
                    showToast(data.message, 'warning');
                }
            })
            .catch(error => console.error('Silme hatası:', error));
        }
    });

    // ==================================================
    // 3. SLIDER VE GÖRSEL
    // ==================================================

    // --- ANA SAYFA HERO SLIDER ---
    if (heroSwiperElement) {
        const heroSwiperInstance = new Swiper('.hero-swiper', {
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
                afterInit: function (swiper) { updateHeaderBackground(swiper); },
                slideChangeTransitionEnd: function (swiper) { updateHeaderBackground(swiper); },
                realIndexChange: function (swiper) { updateHeaderBackground(swiper); }
            }
        });
    }

    // --- YENİ ÜRÜNLER SLIDER ---
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

    // --- HIZLI BAKIŞ (QUICK VIEW) ---
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
                    // Modal İçeriğini Doldur
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

    // Hızlı Ekle Helper (Hover için)
    function buildQuickAddUI(container, variants, baseActionUrl) {
        if (!variants || variants.length === 0) {
            container.innerHTML = '<small class="text-muted p-2 d-block text-center">Seçenek yok.</small>';
            return;
        }
        // Benzersiz renkleri bul
        const uniqueColorObjects = [];
        const seenColorNames = new Set();
        variants.forEach(v => {
            if (v.color && !seenColorNames.has(v.color)) {
                uniqueColorObjects.push({ name: v.color, hex: v.hex_code });
                seenColorNames.add(v.color);
            }
        });
        
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
        initializeQuickAddLogic(container, variants);
    }

    function initializeQuickAddLogic(container, variants) {
        const form = container.querySelector('form');
        const colorSwatches = container.querySelectorAll('.color-swatch');
        const sizeContainer = container.querySelector('.quick-view-sizes');
        const addToCartBtn = container.querySelector('button[type="submit"]');
        let selectedColor = null;
        let currentVariant = null;

        colorSwatches.forEach(swatch => {
            swatch.addEventListener('click', (e) => {
                e.stopPropagation();
                selectedColor = swatch.dataset.color;
                colorSwatches.forEach(s => s.classList.remove('selected'));
                swatch.classList.add('selected');
                updateSizeSwatches(sizeContainer, variants, selectedColor);
                addToCartBtn.disabled = true;
                currentVariant = null;
            });
        });

        sizeContainer.addEventListener('click', (e) => {
            e.stopPropagation();
            const target = e.target;
            if (target.classList.contains('size-swatch') && !target.classList.contains('disabled')) {
                sizeContainer.querySelectorAll('.size-swatch').forEach(s => s.classList.remove('selected'));
                target.classList.add('selected');
                const variantId = target.dataset.variantId;
                currentVariant = variants.find(v => v.id == variantId);
                if (currentVariant) {
                    const baseUrl = form.dataset.baseAction;
                    form.action = baseUrl.replace('0', currentVariant.id);
                    addToCartBtn.disabled = false;
                }
            }
        });
    }

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


    // ==================================================
    // 4. ÜRÜN DETAY SAYFASI (GELİŞMİŞ MANTIK)
    // (Renk Seçimi, Resim Filtreleme, Stok Bildirimi)
    // ==================================================
    const variantsDataEl = document.getElementById('variants-data');
    if (variantsDataEl) {
        try {
            const variantsData = JSON.parse(variantsDataEl.textContent); const variants = variantsData;
            const mainImage = document.getElementById('main-product-image'); 
            const thumbnails = document.querySelectorAll('.thumbnail-img');
            const colorSelector = document.getElementById('color-selector'); 
            const sizeSelector = document.getElementById('size-selector');
            const priceDisplay = document.getElementById('product-price'); 
            const stockDisplay = document.getElementById('product-stock');
            const addToCartBtn = document.getElementById('add-to-cart-btn'); 
            const addToCartForm = document.getElementById('add-to-cart-form');
            const quantityInput = document.getElementById('quantity-input'); 
            const quantityMinusBtn = document.getElementById('quantity-minus'); 
            const quantityPlusBtn = document.getElementById('quantity-plus');
            let selectedColor = null, selectedSize = null, currentVariant = null;

            // Thumbnail Tıklama
            thumbnails.forEach(thumb => {
                thumb.addEventListener('click', function() {
                    if (mainImage) mainImage.src = this.src;
                    thumbnails.forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                });
            });

            // Renk Selector Oluşturma
            if (colorSelector && variants && variants.length > 0) {
                const uniqueColors = [];
                const seenColors = new Set();
                variants.forEach(v => {
                    if (v.color && !seenColors.has(v.color)) {
                        uniqueColors.push({ name: v.color, hex: v.hex_code });
                        seenColors.add(v.color);
                    }
                });
                 
                colorSelector.innerHTML = '';
                uniqueColors.forEach(c => {
                    const div = document.createElement('div');
                    div.className = 'variant-swatch color-swatch';
                    div.dataset.color = c.name;
                    div.style.backgroundColor = c.hex || '#ccc';
                    div.title = c.name;
                    colorSelector.appendChild(div);
                });

                 // Renk Tıklama
                 colorSelector.querySelectorAll('.color-swatch').forEach(swatch => {
                     swatch.addEventListener('click', function() {
                         selectedColor = this.dataset.color;
                         selectedSize = null;
                         
                         colorSelector.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('selected'));
                         this.classList.add('selected');
                         
                         // GALERİYİ FİLTRELE
                         filterGalleryByColor(selectedColor);

                         updateSizeOptions();
                         resetDisplayPartial();
                     });
                 });

                 // --- YENİ: Varsayılan Olarak İlk Rengi Seç ---
                 const firstSwatch = colorSelector.querySelector('.color-swatch');
                 if (firstSwatch) {
                     firstSwatch.click(); // Otomatik tıklama
                 }

            } else if (colorSelector) {
                 colorSelector.innerHTML = '<small class="text-muted">Tek Renk</small>';
                 if(variants.length > 0 && variants[0].color) selectedColor = variants[0].color;
                 updateSizeOptions(); // Tek renkse bedenleri yükle
            }

            // --- YENİLENEN GALERİ FİLTRELEME ---
            function filterGalleryByColor(colorName) {
                let firstVisibleImage = null;
                let foundSpecificImage = false;

                thumbnails.forEach(thumb => {
                    const imgColor = thumb.dataset.color;
                    
                    // 1. Adım: Tam eşleşenleri bul
                    if (imgColor === colorName) {
                        thumb.style.display = 'block';
                        foundSpecificImage = true;
                        if (!firstVisibleImage) firstVisibleImage = thumb.src;
                    } else {
                        thumb.style.display = 'none';
                    }
                });

                // 2. Adım: Eğer o renge ait hiç resim YOKSA, 'all' (Kapak) resimlerini geri aç
                if (!foundSpecificImage) {
                    thumbnails.forEach(thumb => {
                        if (thumb.dataset.color === 'all') {
                            thumb.style.display = 'block';
                            if (!firstVisibleImage) firstVisibleImage = thumb.src;
                        }
                    });
                }

                // Ana resmi güncelle
                if (firstVisibleImage && mainImage) {
                    mainImage.src = firstVisibleImage;
                }
            }

            function updateSizeOptions() {
                if (!sizeSelector || !variants) return;
                sizeSelector.innerHTML = '';
                
                if (!selectedColor && colorSelector.innerHTML.indexOf('color-swatch') !== -1) {
                    sizeSelector.innerHTML = '<small class="text-muted">Önce renk seçiniz.</small>';
                    return;
                }

                const availableVariants = variants.filter(v => !selectedColor || v.color === selectedColor);

                availableVariants.forEach(variant => {
                    const div = document.createElement('div');
                    div.className = 'variant-swatch size-swatch';
                    div.textContent = variant.size;
                    div.dataset.variantId = variant.id;
                    // Stok yoksa özel sınıf ekle (disabled değil)
                    if (variant.stock <= 0) {
                        div.classList.add('out-of-stock');
                        div.title = "Tükendi (Haber Ver)";
                    }
                    sizeSelector.appendChild(div);
                });

                sizeSelector.querySelectorAll('.size-swatch').forEach(swatch => {
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
                     let val = parseInt(quantityInput.value) || 1;
                     if (val > 1) { quantityInput.value = val - 1; updateQuantityButtons(); }
                 });
            }
            if (quantityPlusBtn && quantityInput) {
                 quantityPlusBtn.addEventListener('click', () => {
                     let val = parseInt(quantityInput.value) || 1;
                     if (currentVariant && val < currentVariant.stock) { quantityInput.value = val + 1; updateQuantityButtons(); }
                 });
            }

            function updateQuantityButtons() {
                if (!currentVariant || !quantityInput) return;
                let val = parseInt(quantityInput.value);
                if(quantityMinusBtn) quantityMinusBtn.disabled = val <= 1;
                if(quantityPlusBtn) quantityPlusBtn.disabled = val >= currentVariant.stock;
            }

            function resetDisplayPartial() {
                 if (priceDisplay) priceDisplay.textContent = 'Seçim yapın';
                 if (stockDisplay) { stockDisplay.textContent = ''; stockDisplay.className = ''; }
                 
                 const stockAction = document.getElementById('stock-action-container');
                 const notifyStock = document.getElementById('notify-stock-container');
                 if(stockAction) stockAction.style.display = 'flex';
                 if(notifyStock) notifyStock.style.display = 'none';
                 
                 if (addToCartBtn) addToCartBtn.disabled = true;
                 currentVariant = null;
            }

            function updateDisplay() {
                 const stockAction = document.getElementById('stock-action-container');
                 const notifyStock = document.getElementById('notify-stock-container');
                 const notifyInput = document.getElementById('notify-variant-id');

                 currentVariant = variants.find(v => 
                    (!selectedColor || v.color === selectedColor) && 
                    v.size === selectedSize
                 );
                 
                 if (currentVariant) {
                     if (priceDisplay) priceDisplay.textContent = `${currentVariant.price} TL`;
                     
                     if (currentVariant.stock > 0) {
                         if (stockDisplay) { stockDisplay.textContent = `Stok: ${currentVariant.stock}`; stockDisplay.className = 'text-success fw-bold'; }
                         if(stockAction) stockAction.style.display = 'flex';
                         if(notifyStock) notifyStock.style.display = 'none';
                         if (addToCartBtn) addToCartBtn.disabled = false;
                         if (quantityInput) { quantityInput.max = currentVariant.stock; quantityInput.value = 1; }
                         updateQuantityButtons();
                         if (addToCartForm) {
                             const base = addToCartForm.dataset.baseAction;
                             if (base) addToCartForm.action = base.replace('0', currentVariant.id);
                         }
                     } else {
                         if (stockDisplay) { stockDisplay.textContent = 'Tükendi'; stockDisplay.className = 'text-danger fw-bold'; }
                         if(stockAction) stockAction.style.display = 'none';
                         if(notifyStock) notifyStock.style.display = 'block';
                         if(notifyInput) notifyInput.value = currentVariant.id;
                     }
                 } else {
                    resetDisplayPartial();
                 }
            }
            
        } catch (e) { console.error(e); }
    }

    // --- STOK BİLDİRİM FORMU GÖNDERİMİ ---
    const notifyForm = document.getElementById('notify-stock-form');
    if (notifyForm) {
        notifyForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const btn = this.querySelector('button');
            const originalText = btn.innerText;
            btn.disabled = true; btn.innerText = '...';

            fetch(this.action, {
                method: 'POST', body: new FormData(this),
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(r => r.json())
            .then(data => {
                showToast(data.message, data.status === 'ok' ? 'success' : 'warning');
                if(data.status === 'ok') this.reset();
            })
            .catch(e => showToast('Hata oluştu', 'danger'))
            .finally(() => { btn.disabled = false; btn.innerText = originalText; });
        });
    }

    // ==================================================
    // 5. ÜRÜN LİSTE SAYFASI (GRID, RENK DOTS)
    // ==================================================

// --- LİSTE SAYFASI: RENK HOVER EFEKTİ (DOKUNMATİK UYUMLULUĞU) ---
    const colorDots = document.querySelectorAll('.color-dot-list');
    colorDots.forEach(dot => {
        
        // Touchscreen olmayan cihazlarda (fare olan cihazlarda) çalıştır
        if (!('ontouchstart' in window)) {
            
            // Mouse Enter (Üzerine gelince)
            dot.addEventListener('mouseenter', function() {
                const imgEl = document.getElementById(this.dataset.targetImg);
                if (imgEl && this.dataset.imgSrc) imgEl.src = this.dataset.imgSrc;
            });
            
            // Mouse Leave (Üzerinden çekilince)
            dot.addEventListener('mouseleave', function() {
                const imgEl = document.getElementById(this.dataset.targetImg);
                if (imgEl && imgEl.dataset.originalSrc) imgEl.src = imgEl.dataset.originalSrc;
            });
        }

    // --- HIZLI EKLE PANELİ (Listeleme Sayfası) ---
    const productCards = document.querySelectorAll('.product-list-item .product-card');
    productCards.forEach(card => {
        const quickAddContainer = card.querySelector('.quick-add-section');
        const slug = card.dataset.productSlug;
        let isLoaded = false;

        card.addEventListener('mouseenter', () => {
            if (isLoaded || !slug || !quickAddContainer) return;
            fetch(`/products/quick-view/${slug}/`)
                .then(r => {
                    if (!r.ok) throw new Error('Error');
                    return r.json();
                })
                .then(data => {
                    buildQuickAddUI(quickAddContainer, data.variants, data.add_to_cart_url_base);
                    isLoaded = true;
                })
                .catch(e => {
                    if(quickAddContainer) quickAddContainer.innerHTML = '<small class="text-danger p-2 d-block text-center">...</small>';
                });
        });
    });

    // --- GRID DEĞİŞTİRİCİ ---
    const gridContainer = document.getElementById('product-grid-container');
    const gridSwitches = document.querySelectorAll('.js-grid-switch');

    if (gridContainer && gridSwitches.length > 0) {
        const savedCols = localStorage.getItem('productGridCols');
        if (savedCols) applyGrid(savedCols);

        gridSwitches.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const cols = this.dataset.cols;
                applyGrid(cols);
                localStorage.setItem('productGridCols', cols);
            });
        });

        function applyGrid(cols) {
            gridContainer.classList.remove('row-cols-lg-3', 'row-cols-lg-4');
            if (cols === '4') gridContainer.classList.add('row-cols-lg-4');
            else gridContainer.classList.add('row-cols-lg-3');

            gridSwitches.forEach(btn => {
                if (btn.dataset.cols === cols) {
                    btn.classList.add('active'); btn.classList.remove('text-muted'); btn.classList.add('text-dark');
                } else {
                    btn.classList.remove('active'); btn.classList.add('text-muted'); btn.classList.remove('text-dark');
                }
            });
        }
    }

    // ==================================================
    // 6. CANLI ARAMA
    // ==================================================
    const searchInput = document.getElementById('live-search-input');
    const searchResults = document.getElementById('search-results');
    let searchTimeout;

    if (searchInput && searchResults) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            clearTimeout(searchTimeout);

            if (query.length < 3) {
                searchResults.style.display = 'none';
                return;
            }

            searchTimeout = setTimeout(() => {
                fetch(`/products/live-search/?q=${encodeURIComponent(query)}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.results.length > 0) {
                            let html = '';
                            data.results.forEach(p => {
                                html += `
                                    <a href="${p.url}" class="live-search-item">
                                        <img src="${p.image}" class="live-search-img">
                                        <div class="live-search-info"><h6>${p.name}</h6><span>${p.price} TL</span></div>
                                    </a>`;
                            });
                            html += `<a href="/products/?q=${encodeURIComponent(query)}" class="live-search-item justify-content-center fw-bold text-primary bg-light">Tüm Sonuçları Gör</a>`;
                            searchResults.innerHTML = html;
                        } else {
                            searchResults.innerHTML = '<div class="p-3 text-center text-muted small">Sonuç yok.</div>';
                        }
                        searchResults.style.display = 'block';
                    })
                    .catch(e => console.error(e));
            }, 300);
        });

        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }

}); // DOMContentLoaded