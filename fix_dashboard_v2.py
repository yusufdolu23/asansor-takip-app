#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Eski kodu bul ve değiştir - emoji olmadan dene
old_part1 = 'if len(bakim_list) > 0:\n            df_bakim = pd.DataFrame(bakim_list).tail(10)'
new_part1 = '''if len(bakim_list) > 0:
            son_10_bakim = bakim_list[-10:] if len(bakim_list) > 10 else bakim_list
            df_bakim = pd.DataFrame(son_10_bakim)
            
            display_cols = []
            col_mapping = {}
            
            if 'bakim_tarihi' in df_bakim.columns:
                display_cols.append('bakim_tarihi')
                col_mapping['bakim_tarihi'] = '📅 Tarih'
            if 'bina' in df_bakim.columns:
                display_cols.append('bina')
                col_mapping['bina'] = '🏢 Bina'
            if 'asansor_kimlik' in df_bakim.columns:
                display_cols.append('asansor_kimlik')
                col_mapping['asansor_kimlik'] = '🛗 Asansör'
            if 'yapilan_islem' in df_bakim.columns:
                display_cols.append('yapilan_islem')
                col_mapping['yapilan_islem'] = '⚙️ İşlem'
            if 'teknisyen' in df_bakim.columns:
                display_cols.append('teknisyen')
                col_mapping['teknisyen'] = '👷 Teknisyen'
            if 'durum' in df_bakim.columns:
                display_cols.append('durum')
                col_mapping['durum'] = '📊 Durum'
            
            if display_cols:
                df_display = df_bakim[display_cols].copy()
                df_display = df_display.rename(columns=col_mapping)
                st.dataframe(df_display, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_bakim, use_container_width=True, hide_index=True'''

old_part2 = '''            try:
                st.dataframe(df_bakim[["bina", "asansor_kimlik", "islem", "teknisyen", "tarih"]], 
                           use_container_width=True, hide_index=True)
            except:
                st.dataframe(df_bakim, use_container_width=True, hide_index=True)'''

if old_part1 in content and old_part2 in content:
    content = content.replace(old_part1, new_part1)
    content = content.replace(old_part2, ')')
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Dashboard düzeltildi!")
else:
    print("❌ Kod bulunamadı!")
    print("old_part1 found:", old_part1 in content)
    print("old_part2 found:", old_part2 in content)
