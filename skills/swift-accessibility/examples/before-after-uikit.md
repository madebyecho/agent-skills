# UIKit Before/After Examples

Real-world transformations showing what the swift-accessibility skill produces.

---

## Example 1: Profile View Controller

### Before

```swift
class ProfileViewController: UIViewController {

    let avatarImageView = UIImageView()
    let nameLabel = UILabel()
    let bioLabel = UILabel()
    let editButton = UIButton(type: .system)
    let settingsButton = UIBarButtonItem()

    override func viewDidLoad() {
        super.viewDidLoad()

        avatarImageView.image = UIImage(named: "user-avatar")
        avatarImageView.layer.cornerRadius = 50
        avatarImageView.clipsToBounds = true

        nameLabel.font = UIFont.boldSystemFont(ofSize: 24)
        nameLabel.text = user.name

        bioLabel.font = UIFont.systemFont(ofSize: 14)
        bioLabel.text = user.bio
        bioLabel.numberOfLines = 3

        editButton.setImage(UIImage(systemName: "pencil"), for: .normal)
        editButton.addTarget(self, action: #selector(editProfile), for: .touchUpInside)

        settingsButton.image = UIImage(systemName: "gear")
        settingsButton.target = self
        settingsButton.action = #selector(openSettings)
        navigationItem.rightBarButtonItem = settingsButton
    }
}
```

### After

```swift
class ProfileViewController: UIViewController {

    let avatarImageView = UIImageView()
    let nameLabel = UILabel()
    let bioLabel = UILabel()
    let editButton = UIButton(type: .system)
    let settingsButton = UIBarButtonItem()

    override func viewDidLoad() {
        super.viewDidLoad()

        avatarImageView.image = UIImage(named: "user-avatar")
        avatarImageView.layer.cornerRadius = 50
        avatarImageView.clipsToBounds = true
        avatarImageView.isAccessibilityElement = true
        avatarImageView.accessibilityLabel = "Profile photo" // [VERIFY] confirm label matches intent
        avatarImageView.accessibilityIdentifier = "profileAvatarImage"

        nameLabel.font = UIFont.preferredFont(forTextStyle: .title2)
        nameLabel.adjustsFontForContentSizeCategory = true
        nameLabel.text = user.name
        nameLabel.accessibilityTraits = .header
        nameLabel.accessibilityIdentifier = "profileNameLabel"

        bioLabel.font = UIFont.preferredFont(forTextStyle: .footnote)
        bioLabel.adjustsFontForContentSizeCategory = true
        bioLabel.text = user.bio
        bioLabel.numberOfLines = 3
        bioLabel.accessibilityIdentifier = "profileBioLabel"

        editButton.setImage(UIImage(systemName: "pencil"), for: .normal)
        editButton.addTarget(self, action: #selector(editProfile), for: .touchUpInside)
        editButton.accessibilityLabel = "Edit profile" // [VERIFY] confirm label matches intent
        editButton.accessibilityHint = "Opens the profile editor"
        editButton.accessibilityIdentifier = "editProfileButton"

        settingsButton.image = UIImage(systemName: "gear")
        settingsButton.target = self
        settingsButton.action = #selector(openSettings)
        settingsButton.accessibilityLabel = "Settings" // [VERIFY] confirm label matches intent
        settingsButton.accessibilityIdentifier = "settingsBarButton"
        navigationItem.rightBarButtonItem = settingsButton
    }
}
```

### Changes Summary

| Priority | Issue | Fix |
|----------|-------|-----|
| P0 | Avatar image without label | Added `isAccessibilityElement`, `accessibilityLabel` |
| P0 | Icon-only edit button without label | Added `accessibilityLabel` |
| P0 | Icon-only settings bar button without label | Added `accessibilityLabel` |
| P1 | Edit button without hint | Added `accessibilityHint` |
| P1 | No accessibility identifiers | Added identifiers to all elements |
| P2 | `boldSystemFont(ofSize: 24)` hardcoded | Changed to `preferredFont(forTextStyle: .title2)` |
| P2 | `systemFont(ofSize: 14)` hardcoded | Changed to `preferredFont(forTextStyle: .footnote)` |
| P2 | Missing `adjustsFontForContentSizeCategory` | Added to both labels |
| P2 | Name label missing header trait | Added `.header` trait |

---

## Example 2: Message List Cell

### Before

```swift
class MessageCell: UITableViewCell {

    let senderLabel = UILabel()
    let previewLabel = UILabel()
    let timeLabel = UILabel()
    let unreadIndicator = UIImageView()
    let attachmentIcon = UIImageView()

    func configure(with message: Message) {
        senderLabel.font = UIFont.boldSystemFont(ofSize: 16)
        senderLabel.text = message.senderName

        previewLabel.font = UIFont.systemFont(ofSize: 14)
        previewLabel.text = message.preview
        previewLabel.textColor = .gray

        timeLabel.font = UIFont.systemFont(ofSize: 12)
        timeLabel.text = message.formattedTime

        unreadIndicator.image = UIImage(systemName: "circle.fill")
        unreadIndicator.tintColor = .systemBlue
        unreadIndicator.isHidden = message.isRead

        if message.hasAttachment {
            attachmentIcon.image = UIImage(systemName: "paperclip")
        }
    }
}
```

### After

```swift
class MessageCell: UITableViewCell {

    let senderLabel = UILabel()
    let previewLabel = UILabel()
    let timeLabel = UILabel()
    let unreadIndicator = UIImageView()
    let attachmentIcon = UIImageView()

    func configure(with message: Message) {
        senderLabel.font = UIFont.preferredFont(forTextStyle: .headline)
        senderLabel.adjustsFontForContentSizeCategory = true
        senderLabel.text = message.senderName

        previewLabel.font = UIFont.preferredFont(forTextStyle: .subheadline)
        previewLabel.adjustsFontForContentSizeCategory = true
        previewLabel.text = message.preview
        previewLabel.textColor = .secondaryLabel

        timeLabel.font = UIFont.preferredFont(forTextStyle: .caption1)
        timeLabel.adjustsFontForContentSizeCategory = true
        timeLabel.text = message.formattedTime

        unreadIndicator.image = UIImage(systemName: "circle.fill")
        unreadIndicator.tintColor = .systemBlue
        unreadIndicator.isHidden = message.isRead
        unreadIndicator.isAccessibilityElement = false

        if message.hasAttachment {
            attachmentIcon.image = UIImage(systemName: "paperclip")
            attachmentIcon.isAccessibilityElement = false
        }

        // Combine cell content into a single VoiceOver element
        isAccessibilityElement = true
        accessibilityIdentifier = "messageCell_\(message.id)"

        var label = "From \(message.senderName). \(message.preview). \(message.formattedTime)"
        if !message.isRead { label = "Unread. " + label }
        if message.hasAttachment { label += ". Has attachment" }
        accessibilityLabel = label

        accessibilityCustomActions = [
            UIAccessibilityCustomAction(
                name: "Delete",
                target: self,
                selector: #selector(deleteAction)
            ),
            UIAccessibilityCustomAction(
                name: message.isRead ? "Mark as unread" : "Mark as read",
                target: self,
                selector: #selector(toggleReadAction)
            )
        ]
    }

    @objc private func deleteAction() -> Bool {
        // Delegate to parent for deletion
        return true
    }

    @objc private func toggleReadAction() -> Bool {
        // Delegate to parent for read/unread toggle
        return true
    }
}
```

### Changes Summary

| Priority | Issue | Fix |
|----------|-------|-----|
| P0 | Unread indicator image without label | Hidden from VoiceOver; info included in cell label |
| P0 | Attachment icon without label | Hidden from VoiceOver; info included in cell label |
| P1 | No accessibility identifier | Added `accessibilityIdentifier` |
| P2 | `boldSystemFont(ofSize: 16)` hardcoded | Changed to `preferredFont(forTextStyle: .headline)` |
| P2 | `systemFont(ofSize: 14)` hardcoded | Changed to `preferredFont(forTextStyle: .subheadline)` |
| P2 | `systemFont(ofSize: 12)` hardcoded | Changed to `preferredFont(forTextStyle: .caption1)` |
| P2 | Missing `adjustsFontForContentSizeCategory` | Added to all labels |
| P2 | `.gray` text color (may fail contrast) | Changed to `.secondaryLabel` |
| P2 | Ungrouped cell elements | Combined into single accessible element with custom label |
| P3 | No custom actions for swipe functionality | Added delete and toggle-read custom actions |

---

## Example 3: Custom Rating Control

### Before

```swift
class StarRatingView: UIView {
    var rating: Int = 0 {
        didSet { updateStars() }
    }

    private var starButtons: [UIButton] = []

    override init(frame: CGRect) {
        super.init(frame: frame)
        for i in 0..<5 {
            let button = UIButton()
            button.setImage(UIImage(systemName: "star"), for: .normal)
            button.setImage(UIImage(systemName: "star.fill"), for: .selected)
            button.tag = i + 1
            button.addTarget(self, action: #selector(starTapped(_:)), for: .touchUpInside)
            starButtons.append(button)
            addSubview(button)
        }
    }

    @objc private func starTapped(_ sender: UIButton) {
        rating = sender.tag
    }

    private func updateStars() {
        for button in starButtons {
            button.isSelected = button.tag <= rating
        }
    }
}
```

### After

```swift
class StarRatingView: UIView {
    var rating: Int = 0 {
        didSet {
            updateStars()
            accessibilityValue = "\(rating) out of 5 stars"
        }
    }

    private var starButtons: [UIButton] = []

    override init(frame: CGRect) {
        super.init(frame: frame)

        isAccessibilityElement = true
        accessibilityLabel = "Rating" // [VERIFY] confirm label matches intent
        accessibilityTraits = .adjustable
        accessibilityValue = "\(rating) out of 5 stars"
        accessibilityIdentifier = "starRatingControl"

        for i in 0..<5 {
            let button = UIButton()
            button.setImage(UIImage(systemName: "star"), for: .normal)
            button.setImage(UIImage(systemName: "star.fill"), for: .selected)
            button.tag = i + 1
            button.addTarget(self, action: #selector(starTapped(_:)), for: .touchUpInside)
            button.isAccessibilityElement = false // Individual stars hidden; parent is the accessible element
            starButtons.append(button)
            addSubview(button)
        }
    }

    @objc private func starTapped(_ sender: UIButton) {
        rating = sender.tag
    }

    override func accessibilityIncrement() {
        guard rating < 5 else { return }
        rating += 1
    }

    override func accessibilityDecrement() {
        guard rating > 0 else { return }
        rating -= 1
    }

    private func updateStars() {
        for button in starButtons {
            button.isSelected = button.tag <= rating
        }
    }
}
```
