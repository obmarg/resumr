(function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  define([], function() {
    var SectionItemView;
    return SectionItemView = (function(_super) {

      __extends(SectionItemView, _super);

      function SectionItemView() {
        SectionItemView.__super__.constructor.apply(this, arguments);
      }

      SectionItemView.prototype.template = '#section-item-template';

      return SectionItemView;

    })(Backbone.Marionette.ItemView);
  });

}).call(this);
