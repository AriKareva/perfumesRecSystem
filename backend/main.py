import logging
from db.connection import init_db, Base, db_engine
import logs.models
import users.models
import perfumes.models
import ratings.models
from fastapi import FastAPI
from perfumes.routes import perfumes_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def app_start():
    logger.info("Приложение запускается...")
    init_db()

@app.get('/')
async def root():
    return {'message' : 'Perfumes Recomendarion System'}


app.include_router(perfumes_router)


# INSERT INTO perfumes (name, brand_id, photo, concentration_id, price, description) VALUES
#     -- Chanel
#     ('Chanel N°5', 1, 'https://example.com/chanel_no5.jpg', 4, 12900.00, 
#      'Легендарный парфюм, созданный в 1921 году. Символ женственности и элегантности.'),
    
#     ('Chanel Coco Mademoiselle', 1, 'https://example.com/coco_mademoiselle.jpg', 3, 11500.00,
#      'Современная интерпретация восточного аромата для смелых и уверенных в себе женщин.'),
    
#     ('Bleu de Chanel', 1, 'https://example.com/bleu_de_chanel.jpg', 3, 9500.00,
#      'Древесно-пряный аромат для современного мужчины. Символизирует свободу и уверенность.'),
    
#     -- Dior
#     ('Miss Dior', 2, 'https://example.com/miss_dior.jpg', 3, 11200.00,
#      'Цветочный аромат, посвященный молодости и радости жизни.'),
    
#     ('J''adore', 2, 'https://example.com/jadore.jpg', 3, 12500.00,
#      'Роскошный цветочный парфюм, олицетворяющий женскую силу и чувственность.'),
    
#     ('Dior Sauvage', 2, 'https://example.com/sauvage.jpg', 3, 8900.00,
#      'Свежий амброво-древесный аромат, вдохновленный природными ландшафтами.'),
    
#     -- Guerlain
#     ('Shalimar', 3, 'https://example.com/shalimar.jpg', 4, 13500.00,
#      'Первый восточный парфюм в истории, созданный в 1925 году.'),
    
#     ('La Petite Robe Noire', 3, 'https://example.com/robe_noire.jpg', 3, 9800.00,
#      'Игривый и соблазнительный аромат с нотами вишни и пачули.'),
    
#     -- YSL
#     ('Black Opium', 4, 'https://example.com/black_opium.jpg', 3, 10500.00,
#      'Смелый восточно-цветочный аромат для ночной жизни.'),
    
#     ('Libre', 4, 'https://example.com/libre.jpg', 3, 11200.00,
#      'Парфюм о свободе и уверенности в себе. Лаванда сочетается с ванилью.'),
    
#     -- Gucci
#     ('Gucci Bloom', 7, 'https://example.com/gucci_bloom.jpg', 3, 9200.00,
#      'Цветочный аромат, вдохновленный садами Флоренции.'),
    
#     ('Gucci Guilty', 7, 'https://example.com/gucci_guilty.jpg', 3, 9500.00,
#      'Соблазнительный парфюм для тех, кто не боится быть собой.'),
    
#     -- Tom Ford
#     ('Black Orchid', 13, 'https://example.com/black_orchid.jpg', 4, 18500.00,
#      'Роскошный и загадочный парфюм с нотами черной орхидеи и трюфеля.'),
    
#     ('Tobacco Vanille', 13, 'https://example.com/tobacco_vanille.jpg', 4, 19500.00,
#      'Теплый и уютный аромат с нотами табака, ванили и сухофруктов.'),
    
#     -- Jo Malone
#     ('Wood Sage & Sea Salt', 17, 'https://example.com/wood_sage.jpg', 2, 7500.00,
#      'Свежий аромат, напоминающий о прогулке по пляжу в ветреный день.'),
    
#     ('English Pear & Freesia', 17, 'https://example.com/english_pear.jpg', 2, 7800.00,
#      'Фруктово-цветочный аромат с нотами спелой груши и фрезии.'),
    
#     -- Hermès
#     ('Terre d''Hermès', 5, 'https://example.com/terre.jpg', 3, 10500.00,
#      'Землистый и древесный аромат, вдохновленный природными элементами.'),
    
#     -- Armani
#     ('Acqua di Gio', 11, 'https://example.com/acqua_di_gio.jpg', 3, 8500.00,
#      'Свежий морской аромат, создающий ощущение свободы и легкости.'),
    
#     -- Versace
#     ('Bright Crystal', 10, 'https://example.com/bright_crystal.jpg', 3, 8200.00,
#      'Яркий и фруктово-цветочный аромат для современных женщин.'),
    
#     -- Hugo Boss
#     ('Boss Bottled', 18, 'https://example.com/boss_bottled.jpg', 3, 7900.00,
#      'Классический мужской аромат с яблочными и древесными нотами.');
