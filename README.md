# Multi-Modbus Server Simülasyonu

Bu proje, Python ve PyQt6 kullanılarak geliştirilmiş, aynı anda birden fazla Modbus TCP sunucusunu (Slave cihaz) simüle etmenizi sağlayan bir araçtır. Endüstriyel otomasyon testleri, SCADA sistemleri ve PLC haberleşme denemeleri için tasarlanmıştır.

## Özellikler

*   **Çoklu Sanal Cihaz:** İstenilen sayıda sanal Modbus sunucusu oluşturabilirsiniz.
*   **Özelleştirilebilir Ağ Ayarları:** Her sunucu için ayrı IP adresi ve Port numarası belirleyebilirsiniz.
*   **Otomatik Veri Simülasyonu:** Oluşturulan her cihaz, **Holding Register 1** (Adres 1) değerini her 5 saniyede bir otomatik olarak `0` ve `1` arasında değiştirir. Bu sayede canlı veri akışını test edebilirsiniz.
*   **Kullanıcı Dostu Arayüz:** Sunucuları eklemek, silmek, başlatmak ve durdurmak için modern bir grafik arayüz sunar.
*   **Durum Takibi:** Her sunucunun çalışma durumunu (Running/Stopped) anlık olarak görebilirsiniz.

## Kurulum

Projenin çalışması için Python kurulu olmalıdır.

1.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install -r requirements.txt
    ```

2.  Uygulamayı başlatın:
    ```bash
    python main.py
    ```

## Kullanım

1.  **IP Adresi** ve **Port** kutucuklarına istediğiniz değerleri girin (Örn: `127.0.0.1` ve `5020`).
2.  **Add Server** butonuna tıklayarak listeye ekleyin.
3.  İstediğiniz kadar sunucu ekledikten sonra **Start All** butonu ile hepsini başlatın.
4.  Sunucuları durdurmak için **Stop All**, listeden çıkarmak için **Remove Selected** butonlarını kullanabilirsiniz.

## ⚠️ PLC ve Ağ Bağlantısı Hakkında Önemli Bilgiler

Ağdaki gerçek bir PLC'nin veya başka bir bilgisayarın bu simülasyona bağlanabilmesi için aşağıdaki noktalara dikkat etmelisiniz:

### 1. Localhost (127.0.0.1) Hakkında
Eğer sunucuları `127.0.0.1` IP adresi ile oluşturursanız, bu sunuculara **sadece bu bilgisayar üzerinden** erişilebilir. Ağdaki başka bir cihaz (PLC, HMI vb.) bu sunucuları göremez.

### 2. Ağdaki PLC'nin Bağlanması İçin
Gerçek bir PLC'nin bağlanabilmesi için, sunucuyu bilgisayarınızın **Yerel Ağ IP Adresi** (LAN IP) üzerine kurmalısınız.

1.  Komut satırını açıp `ipconfig` yazarak bilgisayarınızın IP adresini öğrenin (Örneğin: `192.168.1.45`).
2.  Uygulamada sunucu eklerken IP kısmına `127.0.0.1` yerine bu adresi (`192.168.1.45`) yazın.
3.  PLC tarafında, hedef IP olarak bilgisayarınızın IP adresini (`192.168.1.45`) ve belirlediğiniz Port numarasını (Örn: `5020`) girin.
    *   *Not: Standart Modbus portu 502'dir ancak bu portu kullanmak için uygulamayı Yönetici (Admin) olarak çalıştırmanız gerekebilir. 5020 gibi yüksek portlar izin gerektirmez.*

### 3. Birden Fazla Farklı IP Kullanmak (Sanal IP'ler)
Eğer tek bir bilgisayarda birden fazla **farklı** IP adresi (Örn: `192.168.1.50`, `192.168.1.51`...) simüle etmek ve PLC'nin bunlara ayrı ayrı bağlanmasını istiyorsanız:

1.  Windows Ağ Bağlantıları ayarlarından, Ethernet kartınıza **İkincil IP (Secondary IP)** adresleri eklemeniz gerekir.
2.  Bu işlemden sonra, eklediğiniz bu IP adreslerini programda kullanarak sunucular oluşturabilirsiniz.
3.  Böylece PLC, `192.168.1.50` adresine gittiğinde 1. sunucuya, `192.168.1.51` adresine gittiğinde 2. sunucuya erişebilir.
