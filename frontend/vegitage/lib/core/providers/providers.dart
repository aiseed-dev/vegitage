import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:vegitage/core/models/vegetable_image.dart';
import 'package:vegitage/core/models/index_item.dart';
import 'package:vegitage/core/models/vegetable.dart';
import 'package:vegitage/core/repositories/vegetable_repository.dart';

/// アプリ全体で使用するサービスクラス
class VegetableService {
  static final VegetableService _instance = VegetableService._internal();
  factory VegetableService() => _instance;
  VegetableService._internal();

  final IVegetableRepository _repository = AssetVegetableRepository();

  // キャッシュ
  List<IndexItem>? _indexCache;
  final Map<String, Vegetable> _vegetableCache = {};

  /// 全てのインデックス項目を取得
  Future<List<IndexItem>> getAllIndexItems() async {
    if (_indexCache != null) {
      return _indexCache!;
    }
    _indexCache = await _repository.getAllIndexItems();
    return _indexCache!;
  }

  /// 野菜のみのインデックスを取得
  Future<List<IndexItem>> getVegetableIndex() async {
    final items = await getAllIndexItems();
    return items.where((item) => item.type == 'vegetable').toList();
  }

  /// リダイレクト先を取得
  Future<String?> getRedirectTarget(String id) async {
    final items = await getAllIndexItems();
    final targetItem = items.firstWhere(
      (item) => item.id == id,
      orElse: () => IndexItem(id: '', type: ''),
    );
    if (targetItem.type == 'redirect') {
      return targetItem.redirectTo;
    }
    return null;
  }

  /// IDを指定して野菜の詳細を取得
  Future<Vegetable> getVegetableById(String id) async {
    if (_vegetableCache.containsKey(id)) {
      return _vegetableCache[id]!;
    }
    final vegetable = await _repository.getVegetableById(id);
    _vegetableCache[id] = vegetable;
    return vegetable;
  }

  /// 検索フィルタリング
  List<IndexItem> filterVegetables(List<IndexItem> vegetables, String query) {
    if (query.isEmpty) {
      return vegetables;
    }

    final lowerCaseQuery = query.toLowerCase();

    return vegetables.where((item) {
      final searchTarget = [
        item.id.toLowerCase(),
        item.displayName?.toLowerCase() ?? '',
        ...(item.searchKeys ?? []).map((key) => key.toLowerCase())
      ];
      return searchTarget.any((key) => key.contains(lowerCaseQuery));
    }).toList();
  }
}

/// 画像情報を取得するサービス
class ImageService {
  static final ImageService _instance = ImageService._internal();
  factory ImageService() => _instance;
  ImageService._internal();

  final Map<String, List<VegetableImage>> _cache = {};

  Future<List<VegetableImage>> getImageInfo(String imageId, String imageCategory) async {
    final cacheKey = '$imageCategory/$imageId';
    if (_cache.containsKey(cacheKey)) {
      return _cache[cacheKey]!;
    }

    try {
      final uri = Uri.parse('https://aiseed.page/images/$imageCategory/$imageId/info.json');
      final response = await http.get(uri);
      if (response.statusCode == 200) {
        final List<dynamic> jsonList = json.decode(utf8.decode(response.bodyBytes));
        final images = jsonList.map((item) => VegetableImage.fromJson(item)).toList();
        _cache[cacheKey] = images;
        return images;
      } else {
        return [];
      }
    } catch (e) {
      print('Failed to load image info: $e');
      return [];
    }
  }
}

/// グローバルインスタンス
final vegetableService = VegetableService();
final imageService = ImageService();
