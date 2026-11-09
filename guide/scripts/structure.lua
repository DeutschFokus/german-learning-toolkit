-- Pandoc Lua filter for "Your German Journey".
--
--   #  Part title           -> <h1 class="part" data-part="1">   (Part 1, Part 2 …)
--   ## Chapter title        -> <h2 data-chapter="5">             (5, 6, 7 …)
--   ## Something {-}        -> unnumbered chapter (e.g. the closing page)
--
-- The numbers are rendered as small badges by the stylesheet. They are
-- added here (instead of being typed into guide.md) so chapters can be
-- added, removed or reordered without renumbering anything by hand.

local part = 0
local chapter = 0

function Header(el)
  local numbered = not el.classes:includes('unnumbered')

  if el.level == 1 and numbered then
    part = part + 1
    el.classes:insert('part')
    el.attributes['data-part'] = tostring(part)
    table.insert(el.content, 1,
      pandoc.Span({ pandoc.Str('Part ' .. part) }, { class = 'part-num' }))

  elseif el.level == 2 and numbered then
    chapter = chapter + 1
    el.attributes['data-chapter'] = tostring(chapter)
    table.insert(el.content, 1,
      pandoc.Span({ pandoc.Str(tostring(chapter)) }, { class = 'ch-num' }))
  end

  return el
end
