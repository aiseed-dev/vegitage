// lib/features/home/vegetable_list_screen.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:vegitage/core/models/index_item.dart';
import 'package:vegitage/core/providers/providers.dart';
import 'package:vegitage/core/providers/favorites_provider.dart';
import 'package:vegitage/shared/constants/app_strings.dart';

class VegetableListScreen extends StatefulWidget {
  const VegetableListScreen({super.key});

  @override
  State<VegetableListScreen> createState() => _VegetableListScreenState();
}

class _VegetableListScreenState extends State<VegetableListScreen> {
  List<IndexItem>? _vegetables;
  bool _isLoading = true;
  String? _error;
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _loadVegetables();
    favoritesNotifier.addListener(_onFavoritesChanged);
  }

  @override
  void dispose() {
    favoritesNotifier.removeListener(_onFavoritesChanged);
    super.dispose();
  }

  void _onFavoritesChanged() {
    if (mounted) {
      setState(() {});
    }
  }

  Future<void> _loadVegetables() async {
    try {
      final vegetables = await vegetableService.getVegetableIndex();
      if (mounted) {
        setState(() {
          _vegetables = vegetables;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _isLoading = false;
        });
      }
    }
  }

  List<IndexItem> _getSortedVegetables() {
    if (_vegetables == null) return [];

    // 検索フィルタリング
    final filtered = vegetableService.filterVegetables(_vegetables!, _searchQuery);

    // お気に入りを優先してソート
    final sorted = List<IndexItem>.from(filtered);
    sorted.sort((a, b) {
      final isAFavorite = favoritesNotifier.isFavorite(a.id);
      final isBFavorite = favoritesNotifier.isFavorite(b.id);
      if (isAFavorite && !isBFavorite) return -1;
      if (!isAFavorite && isBFavorite) return 1;
      return (a.kanaName ?? '').compareTo(b.kanaName ?? '');
    });

    return sorted;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(AppStrings.vegetableListTitle),
      ),
      body: Column(
        children: [
          // 検索バー
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: TextField(
              decoration: InputDecoration(
                hintText: AppStrings.searchHint,
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
                filled: true,
              ),
              onChanged: (value) {
                setState(() {
                  _searchQuery = value;
                });
              },
            ),
          ),
          Expanded(
            child: _buildContent(),
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    if (_isLoading || favoritesNotifier.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(child: Text('エラーが発生しました: $_error'));
    }

    final sortedVegetables = _getSortedVegetables();

    if (sortedVegetables.isEmpty) {
      return const Center(child: Text('該当する野菜が見つかりません。'));
    }

    return ListView.builder(
      itemCount: sortedVegetables.length,
      itemBuilder: (context, index) {
        final item = sortedVegetables[index];
        final isFavorite = favoritesNotifier.isFavorite(item.id);

        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          child: ListTile(
            title: Text(item.displayName ?? '名前なし'),
            subtitle: Text(
              item.oneliner ?? '',
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            trailing: IconButton(
              icon: Icon(
                isFavorite ? Icons.favorite : Icons.favorite_border,
                color: isFavorite ? Colors.redAccent : null,
              ),
              onPressed: () {
                favoritesNotifier.toggleFavorite(item.id);
              },
            ),
            onTap: () {
              context.push('/vegetables/${item.id}');
            },
          ),
        );
      },
    );
  }
}
