// lib/core/providers/favorites_provider.dart
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// お気に入り野菜のIDリストを管理するChangeNotifier
class FavoritesNotifier extends ChangeNotifier {
  static const _favoritesKey = 'favorite_vegetable_ids';

  List<String> _favorites = [];
  bool _isLoading = true;

  List<String> get favorites => _favorites;
  bool get isLoading => _isLoading;

  FavoritesNotifier() {
    _loadFavorites();
  }

  Future<void> _loadFavorites() async {
    final prefs = await SharedPreferences.getInstance();
    _favorites = prefs.getStringList(_favoritesKey) ?? [];
    _isLoading = false;
    notifyListeners();
  }

  Future<void> toggleFavorite(String vegetableId) async {
    final prefs = await SharedPreferences.getInstance();

    if (_favorites.contains(vegetableId)) {
      _favorites.remove(vegetableId);
    } else {
      _favorites.add(vegetableId);
    }

    await prefs.setStringList(_favoritesKey, _favorites);
    notifyListeners();
  }

  bool isFavorite(String vegetableId) {
    return _favorites.contains(vegetableId);
  }
}

/// グローバルなFavoritesNotifierインスタンス
final favoritesNotifier = FavoritesNotifier();
