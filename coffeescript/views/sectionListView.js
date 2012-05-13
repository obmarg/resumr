(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define(['views/sectionItemView'], function(SectionItemView) {
    var SectionListView;
    return SectionListView = (function(_super) {

      __extends(SectionListView, _super);

      function SectionListView() {
        SectionListView.__super__.constructor.apply(this, arguments);
      }

      SectionListView.prototype.itemView = SectionItemView;

      return SectionListView;

    })(Backbone.Marionette.CollectionView);
  });

}).call(this);
